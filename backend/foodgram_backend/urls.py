from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    FavoriteViewSet,
)


router = routers.DefaultRouter()
router.register(r"tags", TagViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecipeViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("djoser.urls.authtoken")),
    path(
        "api/recipes/<int:id>/favorite/",
        FavoriteViewSet.as_view({"post": "create", "delete": "destroy"}),
    ),
    path("api/", include("djoser.urls")),
    path("api/", include(router.urls)),
]
