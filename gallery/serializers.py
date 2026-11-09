from rest_framework import serializers

from .models import Artwork


class ArtworkSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    tags = serializers.ReadOnlyField()
    medium_label = serializers.ReadOnlyField()
    section_label = serializers.CharField(source="get_section_display", read_only=True)

    class Meta:
        model = Artwork
        fields = [
            "id",
            "slug",
            "title",
            "medium",
            "medium_label",
            "section",
            "section_label",
            "tags",
            "date_display",
            "image",
            "alt_text",
            "display_alt",
            "description",
            "order",
            "created_at",
        ]
