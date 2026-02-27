from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView, LogoutView

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST

from django.core.exceptions import PermissionDenied

from .mixins import SmartUserIsOwnerMixin
from MainPage import models
from MainPage import forms


def error_403(request, exception):
    return render(request, 'users/auth/403.html', status=403)

def error_404(request, exception):
    return render(request, 'users/auth/404.html', status=404)


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            #Обновляем сессию, чтобы юзера не выкинуло из аккаунта
            update_session_auth_hash(request, user)
            messages.success(request, 'Ваш пароль було успішно змінено!')
            return redirect('user-update', pk=user.pk) # Кидаем обратно в настройки
    else:
        form = PasswordChangeForm(request.user)
    
    # Используем тот же контекст, что и в редактировании профиля
    return render(request, 'users/auth/password-change.html', {
        'form': form,
        'cmuser_object': request.user
    })

class CustomLoginView(LoginView):
    template_name = "users/auth/login.html"
    next_page = reverse_lazy("post-list")
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

class CustomRegisterView(FormView):
    template_name = "users/auth/register.html"
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
    
    def get_success_url(self):
        return reverse('post-list') + f'#post-{self.object.pk}'

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

class UpdatePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, UpdateView):
    model = models.Post
    template_name = "posts/post-update.html"
    context_object_name = "post_object"
    form_class = forms.PostForm
    
    def get_success_url(self):
        return reverse('post-list') + f'#post-{self.object.pk}'

class DeletePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, DeleteView):
    model = models.Post
    template_name = "posts/post-delete-confirmation.html"
    success_url = reverse_lazy("post-list")
    context_object_name = "post_object"

    def get_success_url(self):
        return reverse_lazy('post-list')

class PostLikeToggle(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(models.Post, pk=pk)
        post_id = post.id
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

        return _redirect_to_post(request, post_id)


@login_required
@require_POST
def add_reply(request, pk):
    post = get_object_or_404(models.Post, pk=pk)
    text_raw = request.POST.get("text", "").strip()

    form = forms.ReplyForm({"text": text_raw})
    
    if form.is_valid() and text_raw:
        reply = form.save(commit=False)
        reply.post = post
        reply.user = request.user
        reply.save()
    else:
        pass

    return _redirect_to_post(request=request, post_id=post.id)

@login_required
def delete_reply(request, pk):
    reply = get_object_or_404(models.Reply, pk=pk)
    post_id = reply.post.id
    
    if request.user == reply.user or request.user == reply.post.creator or request.user.is_admin:
        reply.delete()
    else:
        raise PermissionDenied

    return _redirect_to_post(request=request, post_id=post_id)

def _redirect_to_post(request, post_id):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        base_url = referer.split('#')[0]
        return redirect(f"{base_url}#post-{post_id}")
    return redirect("post-list")
