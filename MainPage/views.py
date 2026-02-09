from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from MainPage import models
from MainPage import forms

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
    context_object_name = "post_object"

