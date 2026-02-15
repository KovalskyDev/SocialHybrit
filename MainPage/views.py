from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from MainPage import models
from MainPage import forms


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    next_page = reverse_lazy("posts-list")
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

class CustomRegisterView(FormView):
    template_name = "users/register.html"
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy("posts-list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class CreatePostView(CreateView):
    model = models.Posts
    template_name = "posts/post-create.html"
    form_class = forms.PostCreateForm
    success_url = reverse_lazy('posts-list')

class ListPostView(ListView):
    model = models.Posts
    template_name = "posts/post-list.html"
    context_object_name = "posts_objects"

class DetailPostView(DetailView):
    model = models.Posts
    template_name = "posts/post-detail.html"
    context_object_name = "post_object"

class UpdatePostView(UpdateView):
    model = models.Posts
    template_name = "posts/post-update.html"
    context_object_name = "post_object"
    form_class = forms.PostCreateForm
    success_url = reverse_lazy('posts-list')

class DeletePostView(DeleteView):
    model = models.Posts
    template_name = "posts/post-delete-confirmation.html"
    success_url = reverse_lazy("posts-list")
    context_object_name = "post_object"
