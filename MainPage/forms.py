from django import forms
from .models import Post, CustomUser, Reply
from django.contrib.auth.forms import UserCreationForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["name", "about", "media"]

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["text"]

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "age", "gender", "avatar"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем атрибуты прямо в виджет поля
        if 'age' in self.fields:
            self.fields['age'].widget.attrs.update({
                'min': '13',
                'max': '100'
            })