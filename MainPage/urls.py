from django.urls import path
from .views import ListPostView, CreatePostView, DetailPostView, DeletePostView, UpdatePostView
urlpatterns = [
    path("", ListPostView.as_view(), name="posts-list"),
    path("create/", CreatePostView.as_view(), name="post-create"),
    path("<int:pk>", DetailPostView.as_view(), name="post-detail"),
    path("update/<int:pk>", UpdatePostView.as_view(), name="post-update"),
    path("delete/<int:pk>", DeletePostView.as_view(), name="post-delete"),
]
