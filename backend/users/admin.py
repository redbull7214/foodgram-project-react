from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'role')
    list_filter = ('username', 'email')



@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass
