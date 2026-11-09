from django.contrib import admin
from django.utils.html import format_html

from .models import Artwork


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "section", "medium", "is_portrait", "date_display", "is_published", "order")
    list_display_links = ("thumbnail", "title")
    list_editable = ("order", "is_published")
    list_filter = ("section", "medium", "is_portrait", "is_published")
    search_fields = ("title", "description", "date_display")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("preview", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "image", "preview")}),
        ("Details", {"fields": ("section", "medium", "is_portrait", "date_display", "alt_text", "description")}),
        ("Publishing", {"fields": ("is_published", "order")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Preview")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;width:auto;border:1px solid #ccc;" />', obj.image.url)
        return "—"

    @admin.display(description="Image preview")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:320px;width:auto;border:1px solid #ccc;" />', obj.image.url)
        return "Upload an image and save to see a preview."
