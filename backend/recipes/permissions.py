from rest_framework.permissions import IsAuthenticatedOrReadOnly


class IsAuthor(IsAuthenticatedOrReadOnly):
    """Проверка доступа: модератор."""
    message = 'Доступно модератору.'

    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH' or "DELETE":
            return request.user == obj.author
        return True
