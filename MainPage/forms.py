from django import forms
from .models import Posts, CustomUsers
from django.contrib.auth.forms import UserCreationForm

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ["name", "about", "creator"]