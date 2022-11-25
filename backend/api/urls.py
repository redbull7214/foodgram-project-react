from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, FollowListView, FollowViewSet,
                    IngredientsViewSet, RecipeViewSet, TagsViewSet)

app_name = 'api'
router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [

    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        FollowViewSet.as_view(),
        name='subscribe'
    ),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
