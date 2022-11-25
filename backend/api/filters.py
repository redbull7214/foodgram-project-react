from django_filters import rest_framework as filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для рецептов.
    """
    is_favorited = filters.BooleanFilter(
        method='get_favorite',
        label='favorite',
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart__user=self.request.user)
        return queryset


class IngredientsSearchFilter(SearchFilter):
    """
    Фильтр для поиска ингредиентов.
    """
    search_param = 'name'
