from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView, LogoutView

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Case, When, Value, IntegerField

from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage

from .mixins import SmartUserIsOwnerMixin
from MainPage import models
from MainPage import forms

from datetime import timedelta
from django.utils import timezone


def error_403(request, exception):
    return render(request, 'users/auth/403.html', status=403)

def error_404(request, exception):
    return render(request, 'users/auth/404.html', status=404)

def error_405(request, exception):
    return render(request, 'users/auth/405.html', status=405)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        is_sub = False
        if self.request.user.is_authenticated:
            is_sub = self.request.user.is_following(self.object)
        
        context["is_sub"] = is_sub
        return context

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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class ListPostView(ListView):
    model = models.Post
    template_name = "posts/post-list.html"
    context_object_name = "posts_objects"
    paginate_by = 7

    def get_queryset(self):
        user = self.request.user
        # Базовый запрос
        queryset = models.Post.objects.all().select_related('creator')
        
        if user.is_authenticated:
            following_ids = user.subscriptions.values_list('following_id', flat=True)
            fresh_threshold = timezone.now() - timedelta(days=3)
            
            queryset = queryset.annotate(
                priority=Case(
                    When(creator_id__in=following_ids, created_at__gte=fresh_threshold, then=Value(1)),
                    When(creator_id__in=following_ids, then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                )
            ).order_by('priority', '-created_at', '-id') # Тройная сортировка!
        else:
            queryset = queryset.order_by('-created_at', '-id')
            
        return queryset

    def get(self, request, *args, **kwargs):
        # Если это AJAX запрос
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            posts_list = self.get_queryset()
            paginator = Paginator(posts_list, self.paginate_by)
            page_number = request.GET.get('page')

            try:
                page_obj = paginator.get_page(page_number)
            except (EmptyPage, PageNotAnInteger):
                return JsonResponse({'html': '', 'has_next': False})

            # Получаем ID лайков для этой конкретной страницы
            user_liked_posts_ids = []
            if request.user.is_authenticated:
                user_liked_posts_ids = models.Like.objects.filter(
                    user=request.user, 
                    post__in=page_obj # Фильтруем лайки только для постов на этой странице
                ).values_list('post_id', flat=True)

            html = render_to_string('posts/includes/post_items_loop.html', {
                'posts_objects': page_obj,
                'user_liked_posts_ids': user_liked_posts_ids,
                'user': request.user
            }, request=request)

            return JsonResponse({
                'html': html,
                'has_next': page_obj.has_next()
            })

        return super().get(request, *args, **kwargs)


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
        action = request.POST.get('action', 'toggle')

        if action == 'like_only':
            models.Like.objects.get_or_create(post=post, user=request.user)
            liked = True
        else:
            like, created = models.Like.objects.get_or_create(post=post, user=request.user)
            if not created:
                like.delete()
                liked = False
            else:
                liked = True

        # Отдаем только нужные данные
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes_count, # Наш @property из модели
        })


class UserSubscribeToggle(LoginRequiredMixin, View):
    def post(self, request, pk):
        target_user = get_object_or_404(models.CustomUser, pk=pk)

        if request.user == target_user:
            return redirect('user-detail', pk=target_user.pk)

        subscription, created = models.Subscription.objects.get_or_create(following=target_user, follower=request.user)

        if not created:
            subscription.delete()

        return redirect('user-detail', pk=target_user.pk)

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
