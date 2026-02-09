from django.contrib import admin
from .models import Posts, CustomUsers

@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    pass
@admin.register(CustomUsers)
class CustomUsersAdmin(admin.ModelAdmin):
    pass