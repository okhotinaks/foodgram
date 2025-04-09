from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from rest_framework import routers

from .views import TagViewSet, IngredientViewSet, UserViewSet, RecipeViewSet

api_router = routers.DefaultRouter()

api_router.register(r'users', UserViewSet, basename='users')
api_router.register(r'tags', TagViewSet, basename='tags')
api_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
api_router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include((api_router.urls, 'api'))),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
