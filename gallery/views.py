import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny

from .models import Artwork
from .serializers import ArtworkSerializer


class ArtworkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public, read-only API.
    GET /api/artworks/            -> all published pieces
    GET /api/artworks/?medium=ink -> filter by medium
    """

    serializer_class = ArtworkSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        qs = Artwork.objects.filter(is_published=True)
        medium = self.request.query_params.get("medium")
        if medium:
            qs = qs.filter(medium=medium)
        return qs


def gallery_index(request):
    works = Artwork.objects.filter(is_published=True)
    serialized = ArtworkSerializer(works, many=True, context={"request": request}).data
    works_json = json.dumps(list(serialized), cls=DjangoJSONEncoder)
    return render(
        request,
        "gallery/index.html",
        {
            "works_json": works_json,
            "work_count": works.count(),
            "medium_count": works.values("medium").distinct().count(),
        },
    )
