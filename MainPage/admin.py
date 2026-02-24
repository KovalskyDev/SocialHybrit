from django.contrib import admin
from .models import Post, CustomUser, Like, Reply

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass

@admin.register(Like)
class CustomUserAdmin(admin.ModelAdmin):
    pass

@admin.register(Reply)
class CustomUserAdmin(admin.ModelAdmin):
    pass