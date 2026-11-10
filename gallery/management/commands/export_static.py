"""
Render the public gallery to a folder of plain files.

The public site is one page built from the database, and nothing on it
needs a server at request time: filtering and the lightbox are client
side. So it can be served as static files, which is what lets it sit on
free hosting that never sleeps.

    python manage.py export_static            # -> dist/
    python manage.py export_static --out www  # somewhere else

What comes out:

    dist/index.html      the gallery, fully rendered
    dist/404.html        same page, so a bad path still shows the work
    dist/static/...      collectstatic output (hashed, long-cacheable)
    dist/media/...       the artwork images

Admin and the REST API are deliberately not exported. They need a
server; the Render deployment is where they live.
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = "Render the public gallery to a folder of static files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--out", default="dist",
            help="Output folder, relative to the project root. Default: dist",
        )
        parser.add_argument(
            "--host", default="localhost",
            help="Host used while rendering. Must be in ALLOWED_HOSTS.",
        )

    def handle(self, *args, **options):
        out = Path(settings.BASE_DIR) / options["out"]
        host = options["host"]

        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)

        # Build the manifest first: with CompressedManifestStaticFilesStorage
        # the {% static %} tag resolves to hashed filenames, and those only
        # exist once collectstatic has run.
        #
        # Django's admin and DRF ship ~600 files of their own CSS and JS.
        # Neither is part of the public page, and neither is reachable on a
        # static host, so they are left out rather than published.
        call_command(
            "collectstatic", interactive=False, verbosity=0, clear=True,
            ignore_patterns=["admin", "rest_framework"],
        )

        html = self._render(host) + self._stamp()
        (out / "index.html").write_text(html, encoding="utf-8")
        (out / "404.html").write_text(html, encoding="utf-8")

        static_files = self._copy(Path(settings.STATIC_ROOT), out / "static")
        media_files = self._copy(Path(settings.MEDIA_ROOT), out / "media")

        size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
        self.stdout.write(self.style.SUCCESS(
            f"Exported to {out}: {len(html):,} bytes of HTML, "
            f"{static_files} static file(s), {media_files} media file(s), "
            f"{size / 1e6:.1f} MB total."
        ))

    def _stamp(self):
        """A build marker, so you can tell which deploy a page came from.

        Without it, two builds of unchanged content are indistinguishable
        once served, and there is no way to check whether a URL is showing
        the latest deploy or a stale one.
        """
        import datetime, os, subprocess

        sha = os.environ.get("GITHUB_SHA", "")
        if not sha:
            try:
                sha = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    capture_output=True, text=True, timeout=5,
                    cwd=settings.BASE_DIR,
                ).stdout.strip()
            except Exception:
                sha = "unknown"
        when = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"\n<!-- build {sha[:12] or 'unknown'} at {when} -->\n"

    def _render(self, host):
        response = Client(headers={"host": host}).get("/")
        if response.status_code != 200:
            raise RuntimeError(
                f"The homepage returned {response.status_code}, not 200. "
                f"If this is 400, add {host!r} to ALLOWED_HOSTS."
            )
        html = response.content.decode("utf-8")

        # The serializer builds absolute image URLs from the request, which
        # would bake the build machine's hostname into the page. Strip the
        # origin so every reference is root-relative and works on any domain.
        for origin in (f"http://{host}", f"https://{host}"):
            html = html.replace(origin, "")

        if "testserver" in html:
            raise RuntimeError("A build hostname leaked into the page.")
        return html

    def _copy(self, src, dst):
        if not src.is_dir():
            self.stdout.write(self.style.WARNING(f"Nothing to copy from {src}"))
            return 0
        shutil.copytree(src, dst)
        return sum(1 for p in dst.rglob("*") if p.is_file())
