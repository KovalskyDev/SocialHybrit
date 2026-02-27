from django.urls import path
from .views import (ListPostView, CreatePostView, DeletePostView, UpdatePostView, 
                    CustomLoginView, CustomLogoutView, CustomRegisterView, password_change,
                    UpdateCustomUserView, DeleteCustomUserView, DetailCustomUserView,
                    PostLikeToggle, add_reply, delete_reply)
urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", CustomRegisterView.as_view(), name="register"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    
    path("", ListPostView.as_view(), name="post-list"),
    path("posts/create/", CreatePostView.as_view(), name="post-create"),
    path("posts/<int:pk>/update/", UpdatePostView.as_view(), name="post-update"),
    path("posts/<int:pk>/delete/", DeletePostView.as_view(), name="post-delete"),
    path("posts/<int:pk>/like/", PostLikeToggle.as_view(), name="post-like"),

    path("replies/<int:pk>/create/", add_reply, name="add_reply"),
    path("replies/<int:pk>/delete/", delete_reply, name="delete_reply"),

    path("users/<int:pk>/", DetailCustomUserView.as_view(), name="user-detail"),
    path("users/<int:pk>/delete/", DeleteCustomUserView.as_view(), name="user-delete"),
    path("users/<int:pk>/update/", UpdateCustomUserView.as_view(), name="user-update"),

    path("password-change/", password_change, name="password-change"),
]
