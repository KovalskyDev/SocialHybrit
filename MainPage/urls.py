from django.urls import path
from .views import (ListPostView, CreatePostView, DetailPostView, DeletePostView, UpdatePostView, 
                    CustomLoginView, CustomLogoutView, CustomRegisterView)
urlpatterns = [
    path("", CustomLoginView.as_view(), name="login"),
    path("register/", CustomRegisterView.as_view(), name="register"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("posts/", ListPostView.as_view(), name="posts-list"),
    path("posts/create/", CreatePostView.as_view(), name="post-create"),
    path("posts/<int:pk>/", DetailPostView.as_view(), name="post-detail"),
    path("posts/update/<int:pk>/", UpdatePostView.as_view(), name="post-update"),
    path("posts/delete/<int:pk>/", DeletePostView.as_view(), name="post-delete"),
]
