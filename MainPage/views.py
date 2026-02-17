from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from .mixins import SmartUserIsOwnerMixin
from MainPage import models
from MainPage import forms


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    next_page = reverse_lazy("post-list")
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

class CustomRegisterView(FormView):
    template_name = "users/register.html"
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy("post-list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class DeleteCustomUserView(LoginRequiredMixin, SmartUserIsOwnerMixin, DeleteView):
    model = models.CustomUser
    template_name = "users/user-delete-confirmation.html"
    success_url = reverse_lazy("post-list")
    context_object_name = "cmuser_object"
    admin_allowed = False

class DetailCustomUserView(DetailView):
    model = models.CustomUser
    template_name = "users/user-detail.html"
    context_object_name = "cmuser_object"

class UpdateCustomUserView(LoginRequiredMixin, SmartUserIsOwnerMixin, UpdateView):
    model = models.CustomUser
    template_name = "users/user-update.html"
    context_object_name = "cmuser_object"
    form_class = forms.CustomUserUpdateForm
    admin_allowed = False

    def get_success_url(self):
        return reverse("user-detail", kwargs={"pk": self.object.pk})
    

class CreatePostView(LoginRequiredMixin, CreateView):
    model = models.Post
    template_name = "posts/post-create.html"
    form_class = forms.PostCreateForm
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

class ListPostView(ListView):
    model = models.Post
    template_name = "posts/post-list.html"
    context_object_name = "posts_objects"

class DetailPostView(DetailView):
    model = models.Post
    template_name = "posts/post-detail.html"
    context_object_name = "post_object"

class UpdatePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, UpdateView):
    model = models.Post
    template_name = "posts/post-update.html"
    context_object_name = "post_object"
    form_class = forms.PostCreateForm
    
    def get_success_url(self):
        return reverse("post-detail", kwargs={"pk": self.object.pk})

class DeletePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, DeleteView):
    model = models.Post
    template_name = "posts/post-delete-confirmation.html"
    success_url = reverse_lazy("post-list")
    context_object_name = "post_object"
