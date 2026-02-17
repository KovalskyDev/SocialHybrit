from django.contrib import admin
from .models import Post, CustomUser

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass