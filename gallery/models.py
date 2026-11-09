from django.db import models
from django.utils.text import slugify


class Artwork(models.Model):
    class Medium(models.TextChoices):
        GRAPHITE = "graphite", "Graphite"
        INK = "ink", "Ink"
        COL_ERASE = "col-erase", "Col-erase pencil"
        COLOURED_PENCIL = "coloured-pencil", "Coloured pencil"
        ACRYLIC = "acrylic", "Acrylic"
        MIXED = "mixed", "Mixed media"

    class Section(models.TextChoices):
        DESIGN = "design", "Character & costume design"
        STUDIES = "studies", "Studies & process"
        RENDERED = "rendered", "Rendered character work"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    medium = models.CharField(max_length=20, choices=Medium.choices, default=Medium.GRAPHITE)
    section = models.CharField(
        max_length=20,
        choices=Section.choices,
        default=Section.RENDERED,
        help_text="Which part of the portfolio this piece belongs in.",
    )
    is_portrait = models.BooleanField(
        default=True,
        help_text="Tag this piece as a portrait so it shows under the 'Portrait' filter.",
    )
    date_display = models.CharField(
        max_length=40,
        blank=True,
        help_text="How the date should be shown, e.g. '2026' or '18 June 2025'.",
    )
    image = models.ImageField(upload_to="artwork/")
    alt_text = models.CharField(
        max_length=300,
        blank=True,
        help_text="Short description of the image for accessibility. Falls back to the title if left blank.",
    )
    description = models.TextField(blank=True, help_text="Optional longer note about the piece.")
    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers show first. Pieces with the same order fall back to newest first.",
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this piece from the public site without deleting it.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "artwork"
            slug = base_slug
            counter = 1
            while Artwork.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_alt(self):
        return self.alt_text or self.title

    @property
    def tags(self):
        tags = [self.medium, self.section]
        if self.is_portrait:
            tags.append("portrait")
        if self.medium in {self.Medium.COL_ERASE, self.Medium.COLOURED_PENCIL, self.Medium.ACRYLIC}:
            tags.append("colour")
        return tags

    @property
    def medium_label(self):
        return self.get_medium_display()
