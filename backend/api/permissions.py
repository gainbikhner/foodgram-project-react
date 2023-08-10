from rest_framework.permissions import IsAuthenticatedOrReadOnly


class IsAuthor(IsAuthenticatedOrReadOnly):
    """Пользователь является автором объекта."""

    message = "Доступно автору."

    def has_object_permission(self, request, view, obj):
        if request.method == "PATCH" or "DELETE":
            return request.user == obj.author
        return True
