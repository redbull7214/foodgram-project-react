from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Follow, User

from .filters import IngredientsSearchFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import AdminOrReadOnly, AuthorOrModeratorOrAdmin
from .serializers import (CustomUserSerializer, FollowSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShortRecipeSerializer,
                          TagSerializer)
from .utils.generate_pdf import get_shopping_cart


class TagsViewSet(ReadOnlyModelViewSet):
    """
    Вьюсет для тегов.
    """
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    """
    Вьюсет для ингредиентов.
    """
    queryset = Ingredient.objects.all()
    permission_classes = (AdminOrReadOnly, )
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsSearchFilter, )
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """
    Вьюсет для рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrModeratorOrAdmin, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Cart, request.user, pk)
        return self.delete_from(Cart, request.user, pk)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated, ))
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    quantity=Sum('amount')
        )
        return (get_shopping_cart(ingredients))


class CustomUserViewSet(UserViewSet):
    """
    ьюсет для пользователей.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny, )


class FollowViewSet(APIView):
    """
    Вьюсет для подписок.
    """
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = LimitPageNumberPagination

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id == request.user.id:
            return Response(
                {'error': 'Нельзя оформить подписку на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
                user=request.user,
                author_id=user_id
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, id=user_id)
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        get_object_or_404(User, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_204_NO_CONTENT
        )


class FollowListView(ListAPIView):
    """
    Вьюсет для отображения подписок.
    """
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)
