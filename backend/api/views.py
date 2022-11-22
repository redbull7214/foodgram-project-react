from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                            Cart, Tag)
from users.models import Follow, User
from .filters import IngredientsSearchFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import AdminOrReadOnly, AuthorOrModeratorOrAdmin
from .serializers import (IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, 
                          FollowSerializer, CustomUserSerializer,ShortRecipeSerializer, ShoppingCartSerializer)



class TagsViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с тегами.
    Добавить тег может администратор.
    """
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с ингредиентами.
    Добавить ингредиент может администратор.
    """
    queryset = Ingredient.objects.all()
    permission_classes = (AdminOrReadOnly, )
    serializer_class = IngredientSerializer
    filter_backends = [IngredientsSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """
    ViewSet для работы с рецептами.
    Для анонимов разрешен только просмотр рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrModeratorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
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
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)
    # @staticmethod
    # def post_method_for_actions(request, pk, serializers):
    #     data = {'user': request.user.id, 'recipe': pk}
    #     serializer = serializers(data=data, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @staticmethod
    # def delete_method_for_actions(request, pk, model):
    #     user = request.user
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     model_obj = get_object_or_404(model, user=user, recipe=recipe)
    #     model_obj.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

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
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount'
        )
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            TTFont('Lemon', 'data/Lemon.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('Lemon', size=24)
        page.drawString(200, 800, 'Список покупок')
        page.setFont('Lemon', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(75, height, (f'{i}. {name} - {data["amount"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response
    # @action( 
    #     detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    # def download_shopping_cart(self, request):
    #     user = get_object_or_404(User, username=request.user.username)
    #     shopping_cart = user.cart.all()
    #     shopping_dict = {}
    #     for num in shopping_cart:
    #         ingredients_queryset = RecipeIngredient.objects.filter(
    #             recipe__cart__user=request.user).values_list(
    #         'ingredient__name', 'ingredient__measurement_unit',
    #         'amount')
    #         for ingredient in ingredients_queryset:
    #             name = ingredient.ingredients.name
    #             amount = ingredient.amount
    #             measurement_unit = ingredient.ingredients.measurement_unit
    #             if name not in shopping_dict:
    #                 shopping_dict[name] = {
    #                     'measurement_unit': measurement_unit,
    #                     'amount': amount}
    #             else:
    #                 shopping_dict[name]['amount'] = (
    #                     shopping_dict[name]['amount'] + amount)

    #     shopping_list = []
    #     for index, key in enumerate(shopping_dict, start=1):
    #         shopping_list.append(
    #             f'{index}. {key} - {shopping_dict[key]["amount"]} '
    #             f'{shopping_dict[key]["measurement_unit"]}\n')
    #     filename = 'shopping_cart.txt'
    #     response = HttpResponse(shopping_list, content_type='text/plain')
    #     response['Content-Disposition'] = f'attachment; filename={filename}'
    #     return response

from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, get_object_or_404
class CustomUserViewSet(UserViewSet):
    """
    ViewSet для работы с пользователями.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


class FollowViewSet(APIView):
    """
    APIView для добавления и удаления подписки на автора
    """
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitPageNumberPagination

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id == request.user.id:
            return Response(
                {'error': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
                user=request.user,
                author_id=user_id
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на пользователя'},
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
            {'error': 'Вы не подписаны на пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowListView(ListAPIView):
    """
    APIView для просмотра подписок.
    """
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)



# class FavoriteViewSet(ModelViewSet):
#     """
#     Обработка списка избанных рецептов.
#     """
#     queryset = Favorite.objects.all()
#     serializer_class = FavoriteSerializer
#     permission_classes = [IsAuthenticated]


#     def perform_create(self, serializer):
#         user = self.request.user
#         recipe_id = self.kwargs.get('recipe_id')
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         serializer.save(recipe=recipe, user=user)

#     def delete(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         recipe_id = self.kwargs.get('recipe_id')
#         object = get_object_or_404(
#             queryset,
#             recipe=recipe_id,
#             user=self.request.user
#         )
#         self.perform_destroy(object)
#         return Response(status=status.HTTP_204_NO_CONTENT)