"""
Load the curated 2024–2026 portfolio selection.

Twenty-four pieces in three sections, ordered the way a character art director
reads a portfolio: original design work first, studies and process second,
finished rendering last.

    python manage.py load_portfolio            # add/update the 24 pieces
    python manage.py load_portfolio --retire   # ...and unpublish everything else

Re-running is safe: pieces are matched on slug and updated in place rather
than duplicated.
"""

from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from gallery.models import Artwork

SEED_DIR = Path(__file__).resolve().parents[3] / "seed_images" / "portfolio"

D, S, R = "design", "studies", "rendered"

WORKS = [
    # ---- Character & costume design -------------------------------------
    dict(slug="knight-armour-breakdown", file="knight-callouts.jpg", section=D,
         title="Knight — Armour Breakdown", medium="ink", date="February 2026",
         alt="Design sheet of an armoured knight with the helmet, shoulder plates, "
             "neck piece and body armour drawn separately and labelled",
         desc="Helmet, shoulder plates, neck piece and body armour called out from the full figure."),
    dict(slug="knight-full-figure", file="knight-figure.jpg", section=D,
         title="Knight — Full Figure", medium="graphite", date="February 2026",
         alt="Graphite drawing of a knight in full plate armour standing with a longsword",
         desc="Weight carried on the sword; plate shapes following the stride."),
    dict(slug="knight-rendered-pass", file="knight-rendered.jpg", section=D,
         title="Knight — Rendered Pass", medium="ink", date="February 2026",
         alt="Finished ink and graphite rendering of an armoured knight holding a longsword",
         desc="The same design taken to finish, every plate edge resolved."),
    dict(slug="creature-lineup", file="monster-lineup.jpg", section=D,
         title="Creature Lineup", medium="ink", date="March 2026",
         alt="Ink drawing of five creature designs standing together at the same scale",
         desc="Five designs at a common scale — brute, wolf, assassin, mask, staff-bearer."),
    dict(slug="shield-maiden", file="warrior-woman.jpg", section=D,
         title="Shield Maiden", medium="ink", date="February 2026",
         alt="Ink drawing of an armoured woman holding a sword point-down, in a layered skirt",
         desc="Layered skirt and segmented greaves over a classical silhouette."),
    dict(slug="caped-hero-concept", file="hero-caped.jpg", section=D,
         title="Caped Hero Concept", medium="ink", date="March 2026",
         alt="Ink drawing of a caped hero in a crested helm with a high collar",
         desc="Crested helm, high collar, chevron break across the chest."),
    dict(slug="field-uniform-concept", file="hero-uniform.jpg", section=D,
         title="Field Uniform Concept", medium="col-erase", date="November 2025",
         alt="Blue pencil and graphite sheet showing an officer and a helmeted variant of one uniform",
         desc="Officer and helmeted variant of one uniform, worked out together."),

    # ---- Studies & process ----------------------------------------------
    dict(slug="twenty-four-heads", file="head-studies.jpg", section=S,
         title="Twenty-Four Heads", medium="col-erase", date="August 2026",
         alt="Sketchbook page of twenty-four head studies in blue pencil, masked and unmasked",
         desc="One page of head types — ages, builds, masked and unmasked."),
    dict(slug="construction-page", file="sketchbook.jpg", section=S,
         title="Construction Page", medium="col-erase", date="August 2026",
         alt="Sketchbook page showing a figure built in blue pencil before the graphite pass",
         desc="Blue underdrawing before the graphite pass goes down."),
    dict(slug="figure-study", file="anatomy.jpg", section=S,
         title="Figure Study", medium="graphite", date="February 2026",
         alt="Graphite study of a standing male figure built from anatomical structure",
         desc="Standing male built from structure rather than traced contour."),
    dict(slug="sequential-page", file="comic-page.jpg", section=S,
         title="Sequential Page", medium="graphite", date="November 2025",
         alt="Pencilled comic page of six panels ending on a page turn",
         desc="Six panels pencilled through to the page turn."),
    dict(slug="squad-lineup", file="suicide-squad.jpg", section=S,
         title="Squad Lineup", medium="graphite", date="December 2025",
         alt="Graphite drawing of a five-figure cast standing together on one scale line",
         desc="A five-figure cast staged on one scale line."),
    dict(slug="corps-group-shot", file="gl-corps.jpg", section=S,
         title="Corps Group Shot", medium="graphite", date="September 2026",
         alt="Graphite group drawing of seven masked and armoured figures stacked together",
         desc="Seven figures stacked into a single reading silhouette."),
    dict(slug="animal-studies", file="animal-studies.jpg", section=S,
         title="Animal Studies", medium="ink", date="December 2025",
         alt="Ink studies of an elephant, a dog, a turtle and a raptor on one page",
         desc="Elephant, dog, turtle and raptor, direct in ink."),

    # ---- Rendered character work ----------------------------------------
    dict(slug="red-season", file="samurai.jpg", section=R,
         title="Red Season", medium="acrylic", date="October 2025",
         alt="Acrylic painting of a lone samurai on a rock before red autumn trees and distant mountains",
         desc="A lone figure held against the landscape rather than set in front of it."),
    dict(slug="green-lantern-suit-design", file="gl-ink.jpg", section=R,
         title="Green Lantern — Suit Design", medium="ink", date="July 2026",
         alt="Inked full-figure costume design with panelled armour and a lantern emblem",
         desc="Costume worked out in ink: panel breaks, forearm armour, boot build."),
    dict(slug="hawkman-and-hawkgirl", file="hawks.jpg", section=R, portrait=True,
         title="Hawkman & Hawkgirl", medium="graphite", date="April 2026",
         alt="Graphite drawing of two winged, helmeted figures shown as paired busts",
         desc="Paired busts; harness, helm and wing detail."),
    dict(slug="peacemaker", file="peacemaker.jpg", section=R, portrait=True,
         title="Peacemaker", medium="graphite", date="May 2025",
         alt="Graphite drawing of a helmeted figure in a plate carrier aiming a pistol at the viewer",
         desc="Likeness and plate carrier, worked wet-dark in graphite."),
    dict(slug="captain-america-reverse", file="cap-back.jpg", section=R,
         title="Captain America — Reverse", medium="graphite", date="May 2025",
         alt="Graphite drawing of a soldier seen from behind in a star-and-stripe jacket",
         desc="Read entirely from behind: jacket, star field, shield strap."),
    dict(slug="reed-richards", file="mr-fantastic.jpg", section=R, portrait=True,
         title="Reed Richards", medium="graphite", date="July 2025",
         alt="Graphite likeness of a man in a white spacesuit with a number four emblem",
         desc="Likeness study built over a construction grid."),
    dict(slug="magneto", file="magneto.jpg", section=R, portrait=True,
         title="Magneto", medium="coloured-pencil", date="August 2026",
         alt="Coloured pencil bust of a bearded man in a red and blue helmet",
         desc="Helmet bust in coloured pencil."),
    dict(slug="john-stewart", file="john-stewart.jpg", section=R,
         title="John Stewart", medium="graphite", date="August 2026",
         alt="Graphite drawing on black of a bearded Green Lantern mid-punch, "
             "the ring flaring at his fist",
         desc="Worked light-out-of-dark: the figure is what the graphite leaves behind."),
    dict(slug="daredevil", file="daredevil.jpg", section=R,
         title="Daredevil", medium="ink", date="April 2026",
         alt="Inked figure in a horned mask and segmented suit holding two batons",
         desc="Inked figure with the suit seams carried through the pose."),
    dict(slug="captain-marvel", file="captain-marvel.jpg", section=R,
         title="Captain Marvel", medium="coloured-pencil", date="October 2026",
         alt="Coloured pencil full figure of an armoured woman in red, gold and blue, "
             "energy flaring from both fists",
         desc="Hard-surface armour over a female figure, with the light sourced from her hands."),
]


class Command(BaseCommand):
    help = "Load the curated 24-piece portfolio selection."

    def add_arguments(self, parser):
        parser.add_argument(
            "--retire",
            action="store_true",
            help="Unpublish any other pieces so only this selection is public. Nothing is deleted.",
        )

    def handle(self, *args, **options):
        if not SEED_DIR.is_dir():
            self.stderr.write(self.style.ERROR(f"Image folder not found: {SEED_DIR}"))
            return

        created = updated = 0
        for i, w in enumerate(WORKS, start=1):
            path = SEED_DIR / w["file"]
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"Missing file, skipped: {path}"))
                continue

            art, is_new = Artwork.objects.get_or_create(
                slug=w["slug"], defaults={"title": w["title"], "image": ""}
            )
            art.title = w["title"]
            art.section = w["section"]
            art.medium = w["medium"]
            art.date_display = w["date"]
            art.alt_text = w["alt"]
            art.description = w["desc"]
            art.is_portrait = w.get("portrait", False)
            art.order = i
            art.is_published = True

            # Only (re)write the image file when it isn't already in place,
            # so re-running doesn't pile up "name_a1b2c3.jpg" duplicates.
            expected = f"artwork/{w['file']}"
            if is_new or art.image.name != expected:
                art.image.delete(save=False)
                with open(path, "rb") as fh:
                    art.image.save(w["file"], File(fh), save=False)
            art.save()

            created += is_new
            updated += not is_new
            self.stdout.write(("  + " if is_new else "  ~ ") + w["title"])

        msg = f"{created} created, {updated} updated."

        if options["retire"]:
            slugs = [w["slug"] for w in WORKS]
            n = Artwork.objects.exclude(slug__in=slugs).filter(is_published=True).update(
                is_published=False
            )
            msg += f" {n} older piece(s) unpublished (still in the database)."

        self.stdout.write(self.style.SUCCESS("Done. " + msg))
