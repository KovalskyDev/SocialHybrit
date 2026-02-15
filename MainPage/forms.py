from django import forms
from .models import Posts, CustomUsers
from django.contrib.auth.forms import UserCreationForm

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ["name", "about", "creator"]

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUsers
        fields = ["username", "email",]

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUsers
        fields = ["email", "first_name", "last_name", "age", "gender",]