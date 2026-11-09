from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"artworks", views.ArtworkViewSet, basename="artwork")

urlpatterns = [
    path("", views.gallery_index, name="gallery-index"),
    path("api/", include(router.urls)),
]
