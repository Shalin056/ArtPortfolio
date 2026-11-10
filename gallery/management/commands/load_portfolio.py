"""
Load the curated 2023-2026 portfolio selection.

Thirty-one pieces in three sections, ordered the way a character art director
reads a portfolio: original design work first, studies and process second,
finished rendering last.

    python manage.py load_portfolio            # add/update the pieces
    python manage.py load_portfolio --retire   # ...and unpublish everything else

Re-running is safe: pieces are matched on slug and updated in place rather
than duplicated.
"""

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from gallery.models import Artwork

SEED_DIR = Path(__file__).resolve().parents[3] / "seed_images" / "portfolio"

D, S, R = "design", "studies", "rendered"

WORKS = [
    # ---- Character & costume design -------------------------------------
    dict(slug="character-concepts", file="character-concepts.jpg", section=D,
         title="Shalin Bhavsar Character Concepts #01 Ink", medium="ink", date="April 2026",
         alt="Ink sheet of original armoured figures with a bald head study worked out alongside",
         desc="Original designs: armour plating, harness and belt rig worked out on the page."),
    dict(slug="gl-suit-design", file="gl-ink.jpg", section=D,
         title="Shalin Bhavsar Green Lantern #02 Ink", medium="ink", date="July 2026",
         alt="Inked full-figure costume design with panelled armour and a lantern emblem on the chest",
         desc="Costume resolved in ink: panel breaks, forearm armour, boot build."),
    dict(slug="gl-figure-design", file="gl-figure.jpg", section=D,
         title="Shalin Bhavsar Green Lantern #03 Ink", medium="ink", date="July 2026",
         alt="Inked full-figure costume design walking forward, lighter line than the finished pass",
         desc="The same suit two days earlier, still finding the walk and the panel seams."),
    dict(slug="gl-colour-design", file="gl-colour.jpg", section=D,
         title="Shalin Bhavsar Green Lantern #04 Coloured pencil", medium="coloured-pencil", date="September 2026",
         alt="Coloured pencil full figure of a green and black costumed flier, ring hand forward",
         desc="The design taken to colour, flying, with the ring as the light source."),
    dict(slug="captain-marvel", file="captain-marvel.jpg", section=D,
         title="Shalin Bhavsar Captain Marvel #05 Coloured pencil", medium="coloured-pencil", date="October 2026",
         alt="Coloured pencil full figure of an armoured woman in red, gold and blue, energy flaring from both fists",
         desc="Hard-surface armour over a female figure, with the light sourced from her hands."),
    dict(slug="jay-garrick", file="jay-garrick.jpg", section=D,
         title="Shalin Bhavsar Jay Garrick #06 Coloured pencil", medium="coloured-pencil", date="October 2026",
         alt="Coloured pencil figure of a man in a red shirt, denim and a winged tin helmet, arms folded",
         desc="Period costume: tin helmet, rolled denim, boots, built as clothing rather than a suit."),
    dict(slug="incredibles-sheet", file="incredibles.jpg", section=D,
         title="Shalin Bhavsar The Incredibles #07 Coloured pencil", medium="coloured-pencil", date="August 2026",
         alt="Coloured pencil sheet of three costumed figures in red and blue on one page",
         desc="Three related costumes on one sheet, sharing a palette and a mask shape."),

    # ---- Studies & process ----------------------------------------------
    dict(slug="construction-page", file="sketchbook.jpg", section=S,
         title="Shalin Bhavsar Construction Page #08 Sketch", medium="col-erase", date="August 2026",
         alt="Sketchbook page of blue pencil figure construction with graphite head studies alongside",
         desc="Blue underdrawing before the graphite pass goes down."),
    dict(slug="hulk-construction", file="hulk-construction.jpg", section=S,
         title="Shalin Bhavsar Hulk #09 Sketch", medium="col-erase", date="August 2026",
         alt="Red col-erase pencil study of a heavily muscled figure standing, drawn as masses",
         desc="A heavy build blocked in red pencil: mass first, contour last."),
    dict(slug="inking-exercises", file="inking-exercises.jpg", section=S,
         title="Shalin Bhavsar Inking Exercises #10 Ink", medium="ink", date="December 2025",
         alt="Page of inked drills: spheres, cubes, cylinders, barrels, books and an eye, each rendered in hatching",
         desc="Form drills in ink. The same hatching logic carries the costume work."),
    dict(slug="animal-studies", file="animal-studies.jpg", section=S,
         title="Shalin Bhavsar Animal Studies #11 Ink", medium="ink", date="December 2025",
         alt="Ink studies of an elephant, a dog, a turtle, a raccoon and a raptor on one page",
         desc="Elephant, dog, turtle, raccoon and raptor, direct in ink."),
    dict(slug="corps-group-shot", file="gl-corps.jpg", section=S,
         title="Shalin Bhavsar Green Lantern Corps #12 Pencil", medium="graphite", date="September 2026",
         alt="Graphite group drawing of eight masked and armoured figures stacked into one mass",
         desc="Eight figures stacked into a single reading silhouette."),
    dict(slug="nightwing", file="nightwing.jpg", section=S,
         title="Shalin Bhavsar Nightwing #13 Pencil", medium="graphite", date="November 2025",
         alt="Loose graphite gesture of an acrobatic figure crouched mid-turn holding a curved sword",
         desc="Kept at gesture stage: the action matters more than the finish."),
    dict(slug="omni-man", file="omni-man.jpg", section=S,
         title="Shalin Bhavsar Omni-Man #14 Pencil", medium="graphite", date="April 2026",
         alt="Graphite full figure of a moustached caped man striding forward, cape falling behind",
         desc="Testing how much weight a cape can carry without stealing the pose."),

    # ---- Rendered character work ----------------------------------------
    dict(slug="red-season", file="samurai.jpg", section=R,
         title="Shalin Bhavsar Samurai #15 Painting", medium="acrylic", date="October 2025",
         alt="Acrylic painting of a lone samurai on a rock before red autumn trees and distant mountains",
         desc="A lone figure held against the landscape rather than set in front of it."),
    dict(slug="batman-knightmare", file="batman-knightmare.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Batman #16 Pencil", medium="graphite", date="January 2023",
         alt="Graphite portrait of a masked figure in a cowl with goggles pushed up on the brow",
         desc="The earliest piece here, kept for the eyes inside the cowl."),
    dict(slug="peacemaker", file="peacemaker.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Peacemaker #17 Pencil", medium="graphite", date="May 2025",
         alt="Graphite drawing of a helmeted figure in a plate carrier aiming a pistol at the viewer",
         desc="Likeness and plate carrier, worked wet-dark in graphite."),
    dict(slug="captain-america-reverse", file="cap-back.jpg", section=R,
         title="Shalin Bhavsar Captain America #18 Pencil", medium="graphite", date="May 2025",
         alt="Graphite drawing of a soldier seen from behind in a star-and-stripe jacket",
         desc="Read entirely from behind: jacket, star field, shield strap."),
    dict(slug="reed-richards", file="mr-fantastic.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Mr. Fantastic #19 Pencil", medium="graphite", date="July 2025",
         alt="Graphite likeness of a man in a white spacesuit with a number four emblem",
         desc="Likeness study built over a construction grid."),
    dict(slug="batman-ink", file="batman-ink.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Batman #20 Ink", medium="ink", date="December 2025",
         alt="Brush-inked bust of a caped figure in a horned cowl, worked in solid blacks",
         desc="Solid blacks, almost no line: the cowl is cut out of the dark."),
    dict(slug="superman-ink", file="superman-ink.jpg", section=R,
         title="Shalin Bhavsar Superman #21 Ink", medium="ink", date="December 2025",
         alt="Inked figure seen from below flying upward, chest emblem catching the light",
         desc="Shot from below with the emblem as the one solid shape."),
    dict(slug="cyclops-ink", file="cyclops-ink.jpg", section=R,
         title="Shalin Bhavsar Cyclops #22 Ink", medium="ink", date="February 2026",
         alt="Inked figure in a visor and tactical harness raising a hand to the visor",
         desc="Hand to the visor: the gesture that makes the costume legible."),
    dict(slug="magneto-ink", file="magneto-ink.jpg", section=R,
         title="Shalin Bhavsar Magneto #23 Ink", medium="ink", date="February 2026",
         alt="Inked figure in a cape and helmet hovering with arms out, cape spread wide",
         desc="Cape spread as a frame around a small, still figure."),
    dict(slug="flash-run", file="flash-run.jpg", section=R,
         title="Shalin Bhavsar Flash #24 Ink", medium="ink", date="February 2026",
         alt="Figure in a lightning-bolt suit running flat out, speed streaks raking the background",
         desc="Everything in the drawing rakes one way, including the background."),
    dict(slug="antman-wasp", file="antman-wasp.jpg", section=R,
         title="Shalin Bhavsar Ant-Man & Wasp #25 Ink", medium="ink", date="March 2026",
         alt="Inked bust of a helmeted figure with a tiny winged figure perched on his shoulder",
         desc="Two characters at wildly different scale, sharing one silhouette."),
    dict(slug="hawkman-ink", file="hawkman-ink.jpg", section=R,
         title="Shalin Bhavsar Hawkman #26 Ink", medium="ink", date="April 2026",
         alt="Inked winged figure in a hawk helm diving with a spiked mace",
         desc="Every feather inked individually so the wings still read as one shape."),
    dict(slug="hawkman-and-hawkgirl", file="hawks.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Hawkman & Hawkgirl #27 Pencil", medium="graphite", date="April 2026",
         alt="Graphite drawing of two winged, helmeted figures shown as paired busts",
         desc="Paired busts; harness, helm and wing detail."),
    dict(slug="cyclops-graphite", file="cyclops-graphite.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Cyclops #28 Pencil", medium="graphite", date="July 2026",
         alt="Graphite portrait of a man in a dark visor and high-collared tactical suit",
         desc="The same character as the ink version, resolved as a likeness."),
    dict(slug="cyclops-colour", file="cyclops-colour.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Cyclops #29 Coloured pencil", medium="coloured-pencil", date="August 2026",
         alt="Coloured pencil portrait of a man in a yellow and red visor over a blue suit",
         desc="Third pass at one character, this time carried by colour."),
    dict(slug="batman-colour", file="batman-colour.jpg", section=R,
         title="Shalin Bhavsar Batman #30 Coloured pencil", medium="coloured-pencil", date="August 2026",
         alt="Coloured pencil drawing of a caped figure in a blue cowl with a red emblem on grey armour",
         desc="Blue over grey, with the emblem the only warm note."),
    dict(slug="magneto", file="magneto.jpg", section=R, portrait=True,
         title="Shalin Bhavsar Magneto #31 Coloured pencil", medium="coloured-pencil", date="August 2026",
         alt="Coloured pencil bust of a bearded older man in a red and blue helmet",
         desc="An older face under a hard-surface helm, with the age carried in coloured pencil."),
]


class Command(BaseCommand):
    help = "Load the curated portfolio selection."

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
            # The name matching the expectation isn't enough - the file itself
            # has to be on disk, or an emptied media folder is never refilled.
            expected = f"artwork/{w['file']}"
            on_disk = Path(settings.MEDIA_ROOT) / expected
            if is_new or art.image.name != expected or not on_disk.exists():
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
