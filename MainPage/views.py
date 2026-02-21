from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from .mixins import SmartUserIsOwnerMixin
from MainPage import models
from MainPage import forms


def error_403(request, exception):
    return render(request, '403.html', status=403)

def error_404(request, exception):
    return render(request, '404.html', status=404)


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
    form_class = forms.PostForm
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

class ListPostView(ListView):
    model = models.Post
    template_name = "posts/post-list.html"
    context_object_name = "posts_objects"

    def get_context_data(self, **kwargs):
        '''Добавление лайкнутых постов в контекст один раз
        для того чтобы не делать много запросов в БД'''
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # получаем список ID всех лайкнутых постов
            context['user_liked_posts_ids'] = models.Like.objects.filter(
                user=self.request.user
            ).values_list('post_id', flat=True)
        return context

class DetailPostView(DetailView): # убрать(заменил логику на то шо теперь это не нужно, а перекидывает на пост-лист с якорем)
    model = models.Post
    template_name = "posts/post-detail.html"
    context_object_name = "post_object"

class UpdatePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, UpdateView):
    model = models.Post
    template_name = "posts/post-update.html"
    context_object_name = "post_object"
    form_class = forms.PostForm
    
    def get_success_url(self):
        return reverse("post-detail", kwargs={"pk": self.object.pk})

class DeletePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, DeleteView):
    model = models.Post
    template_name = "posts/post-delete-confirmation.html"
    success_url = reverse_lazy("post-list")
    context_object_name = "post_object"

class PostLikeToggle(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(models.Post, pk=pk)
        # Получаем тип действия из скрытого поля формы
        action = request.POST.get('action', 'toggle')

        if action == 'like_only':
            # Только создаем, если его еще нет
            models.Like.objects.get_or_create(post=post, user=request.user)
        else:
            # Обычный toggle для кнопки
            like, created = models.Like.objects.get_or_create(post=post, user=request.user)
            if not created:
                like.delete()

        return redirect(request.META.get('HTTP_REFERER', 'post-list'))