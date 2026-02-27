from django.urls import path
from .views import PostListAPI

urlpatterns = [
    path("posts", PostListAPI.as_view(), name="post-list-api")
]
