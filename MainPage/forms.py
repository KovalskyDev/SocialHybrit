from django import forms
from .models import Post, CustomUser
from django.contrib.auth.forms import UserCreationForm

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["name", "about",]

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "age", "gender",]