from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsAuthorPatchDelete(IsAuthenticatedOrReadOnly):
    """Автор может править и удалять свой объект."""

    message = "Доступно только автору."

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user == obj.author
