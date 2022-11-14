from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ACCESS_RIGHTS_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR)
    ]

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,        
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    role = models.CharField(
        'Права доступа',
        choices=ACCESS_RIGHTS_CHOICES,
        default=USER,
        max_length=max([len(x) for x, _ in ACCESS_RIGHTS_CHOICES]),
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        help_text=('Введите пароль'),
    )


    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()

    @property
    def access_moderator(self):
        return self.role == self.MODERATOR

    @property
    def access_administrator(self):
        return self.role == self.ADMIN or self.is_superuser
        

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow unique',
            )
        ]