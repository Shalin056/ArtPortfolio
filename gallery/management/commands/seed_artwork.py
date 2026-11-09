from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from gallery.models import Artwork

SEED_DIR = Path(__file__).resolve().parent.parent.parent.parent / "seed_images"

WORKS = [
    dict(title="A premonition", medium="graphite", is_portrait=True, date_display="2022",
         file="batman-goggles.jpg",
         alt_text="Graphite portrait study of a masked figure wearing flight goggles", order=1),
    dict(title="The soldier", medium="graphite", is_portrait=True, date_display="2024",
         file="captain-america-helmet.jpg",
         alt_text="Graphite portrait of a helmeted figure with a star emblem", order=2),
    dict(title="Portrait study", medium="graphite", is_portrait=True, date_display="2024",
         file="portrait-boy.jpg",
         alt_text="Graphite portrait of a smiling young man wearing glasses", order=3),
    dict(title="Armored and roaring", medium="ink", is_portrait=False, date_display="2026",
         file="batman-armored.jpg",
         alt_text="Ink illustration of a heavily armored caped figure holding an axe", order=4),
    dict(title="Vision", medium="ink", is_portrait=False, date_display="2026",
         file="vision.jpg",
         alt_text="Ink illustration of a caped android figure with a gem set in the forehead, in flight", order=5),
    dict(title="One eyed boy scout", medium="ink", is_portrait=False, date_display="2026",
         file="cyclops.jpg",
         alt_text="Ink illustration of a figure wearing a red visor, adjusting it with one hand", order=6),
    dict(title="Nightwing", medium="ink", is_portrait=False, date_display="2026",
         file="nightwing.jpg",
         alt_text="Ink illustration of a masked acrobat crouched with an escrima stick and a sword", order=7),
    dict(title="Ring-bearer I", medium="ink", is_portrait=False, date_display="2026",
         file="green-lantern-1.jpg",
         alt_text="Ink illustration of a figure in an armored suit with a lantern emblem, fist raised", order=8),
    dict(title="Ring-bearer II", medium="ink", is_portrait=False, date_display="2026",
         file="green-lantern-2.jpg",
         alt_text="Ink illustration of a figure in an armored suit with a lantern emblem, fist to chest", order=9),
    dict(title="A mission", medium="graphite", is_portrait=False, date_display="2025",
         file="captain-america-flag-back.jpg",
         alt_text="Graphite drawing of a soldier from behind, wearing a flag-emblazoned jacket", order=10),
    dict(title="Shield at rest", medium="graphite", is_portrait=True, date_display="2025",
         file="captain-america-profile.jpg",
         alt_text="Graphite portrait in profile of a soldier holding a star-emblazoned shield", order=11),
    dict(title="The Corp", medium="graphite", is_portrait=False, date_display="2026",
         file="green-lantern-corps.jpg",
         alt_text="Graphite group portrait of seven masked and armored figures", order=12),
]


class Command(BaseCommand):
    help = ("Seed the 2022-2026 starter set. Superseded by `load_portfolio`, "
            "which loads the curated selection the live site uses.")

    def handle(self, *args, **options):
        created_count = 0
        for w in WORKS:
            if Artwork.objects.filter(title=w["title"]).exists():
                self.stdout.write(f"Skipping (already exists): {w['title']}")
                continue

            image_path = SEED_DIR / w["file"]
            if not image_path.exists():
                self.stdout.write(self.style.WARNING(f"Missing file, skipped: {image_path}"))
                continue

            artwork = Artwork(
                title=w["title"],
                medium=w["medium"],
                is_portrait=w["is_portrait"],
                date_display=w["date_display"],
                alt_text=w["alt_text"],
                order=w["order"],
            )
            with open(image_path, "rb") as f:
                artwork.image.save(w["file"], File(f), save=True)

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Created: {w['title']}"))

        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} piece(s) created."))
