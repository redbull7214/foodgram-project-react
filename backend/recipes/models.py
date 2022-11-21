from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )
    class Meta:
        # verbose_name = 'Ингридиент'
        # verbose_name_plural = 'Ингридиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='ingredient uniq')]

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ['-id']
        # verbose_name = 'Тег'
        # verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag, 
        related_name='recipes',
        verbose_name='Тег', 
    )
    author = models.ForeignKey(
        User,
        null=True,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        'Название', 
        max_length=200
    )
    image = models.ImageField(
        'Картинка', 
        upload_to='images/',
        null=True,
        blank=True
    )
    text = models.TextField(
        'Описание рецепта'
    )
        
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1, message='Минимальное время приготовления не меньше 1-ой минуты'),
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации', 
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        # verbose_name = 'Рецепт'
        # verbose_name_plural = 'Рецепты'
        

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='RecipeIngredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='RecipeIngredient',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            1, message='Количество не может быть меньше чем 1'),
        ]
    )

    class Meta:
        ordering = ['-id']
        # verbose_name = 'Количество ингридиента'
        # verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_recipe_ingredients'
            )
        ]

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        # verbose_name = 'Корзина'
        # verbose_name_plural = 'В корзине'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_cart'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        # verbose_name = 'Избранное'
        # verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorites'
            )
        ]
