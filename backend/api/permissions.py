from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа:
        - Для анономных пользователей: доступ только к безопасным методам.
        - Для авторизованных пользователей: доступ к безопасным методам,
        а также право редактировать или удалять свои объекты.
        - Для авторов объекта: могут редактировать и удалять свои объекты.
        - Для администраторов: могут редактировать и удалять любые объекты.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
