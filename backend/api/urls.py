from django.urls import include, path
from rest_framework import routers

from api.views import (
    FavoriteViewSet,
    FollowViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
    UserMeViewSet,
)


app_name = "api"

router = routers.DefaultRouter()
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "recipes/<int:id>/favorite/",
        FavoriteViewSet.as_view({"post": "create", "delete": "destroy"}),
    ),
    path(
        "recipes/download_shopping_cart/",
        ShoppingCartViewSet.as_view({"get": "retrieve"}),
    ),
    path(
        "recipes/<int:id>/shopping_cart/",
        ShoppingCartViewSet.as_view({"post": "create", "delete": "destroy"}),
    ),
    path("users/subscriptions/", FollowViewSet.as_view({"get": "list"})),
    path("users/me/", UserMeViewSet.as_view({"get": "retrieve"})),
    path(
        "users/<int:id>/subscribe/",
        FollowViewSet.as_view({"post": "create", "delete": "destroy"}),
    ),
    path("", include("djoser.urls")),
    path("", include(router.urls)),
]
