from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_datetime

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
from django.db.models import Count
from django.db.models import Prefetch

from django.core.exceptions import PermissionDenied

from django.core.paginator import EmptyPage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

"""
CASTOMUSER AUTH
"""

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

"""
CASTOMUSER CBV
"""
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
            context["favorites"] = self.request.user.favorite_posts.count()
        
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
    

class UserSubscribeToggle(LoginRequiredMixin, View):
    def post(self, request, pk):
        target_user = get_object_or_404(models.CustomUser, pk=pk)

        if request.user == target_user:
            return redirect('user-detail', pk=target_user.pk)

        subscription, created = models.Subscription.objects.get_or_create(following=target_user, follower=request.user)

        if not created:
            subscription.delete()

        return redirect('user-detail', pk=target_user.pk)
    
"""
POST CBV
"""
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
    paginate_by = 7

    def get_queryset(self):
        user = self.request.user
        queryset = models.Post.objects.all().select_related('creator')
        
        post_id = self.request.GET.get("post")
        conditions = []

        # 3. Если в URL есть ID поста, вешаем его на самый верх (Приоритет 0)
        if post_id and post_id.isdigit():
            conditions.append(When(pk=int(post_id), then=Value(0)))

        if user.is_authenticated:
            following_ids = user.subscriptions.values_list('following_id', flat=True)
            fresh_threshold = timezone.now() - timedelta(days=3)
            now_threshold = timezone.now() - timedelta(seconds=5)

            conditions.append(When(creator_id=user.id, created_at__gte=now_threshold, then=Value(1))) # (Приоритет 1) если только-что созданный пост(5 секунд) - твой
            conditions.append(When(creator_id__in=following_ids, created_at__gte=fresh_threshold, then=Value(2))) # (Приоритет 2) если твои подписчики что-то запостили И сортировка по самому новому посту
            conditions.append(When(creator_id__in=following_ids, then=Value(3))) # (Приоритет 3) если твои подписчики что-то запостили
        
        queryset = queryset.annotate(
            priority=Case(
                *conditions,
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('priority', '-created_at', '-id')

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['user_liked_posts_ids'] = models.Like.objects.filter(
                user=self.request.user,
                post__in=context['posts_objects'] # Только для постов на текущей странице
            ).values_list('post_id', flat=True)
        else:
            context['user_liked_posts_ids'] = []
            
        return context
class UpdatePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, UpdateView):
    model = models.Post
    form_class = forms.PostForm
    template_name = "posts/post-update.html"
    context_object_name = "post_object"

    def get_success_url(self):
        url = reverse("post-list")
        return f"{url}?post={self.object.pk}"

class DeletePostView(LoginRequiredMixin, SmartUserIsOwnerMixin, DeleteView):
    model = models.Post
    template_name = "posts/post-delete-confirmation.html"
    success_url = reverse_lazy("post-list")
    context_object_name = "post_object"
    success_url = reverse_lazy('post-list')

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

        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes_count,
        })

class PostFavoriteToggle(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(models.Post, pk=pk)

        if post.favorites.filter(id=request.user.id).exists():
            post.favorites.remove(request.user)
            favourited = False
        else:
            post.favorites.add(request.user)
            favourited = True
        
        return JsonResponse({
            'favourited': favourited
        })


"""
REPLY
"""
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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(
                'posts/includes/replies_ajax.html',
                {
                    'replies': [reply],
                    'user': request.user,
                    'post': post
                },
                request=request
            )
            return JsonResponse({
                'status': 'success',
                'html': html,
                'pk': reply.pk,
            })

    return _redirect_to_post(request=request, post_id=post.id)

@login_required
@require_POST
def delete_reply(request, pk):
    reply = get_object_or_404(models.Reply, pk=pk)
    post_id = reply.post.id
    
    if request.user == reply.user or request.user == reply.post.creator or request.user.is_admin:
        reply_id = reply.pk
        reply.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'reply_id': reply_id})
    else:
        raise PermissionDenied

    return _redirect_to_post(request=request, post_id=post_id)


def _redirect_to_post(request, post_id):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        base_url = referer.split('#')[0]
        return redirect(f"{base_url}#post-{post_id}")
    return redirect("post-list")


def get_social_updates(request):
    raw_ids = request.GET.get('ids', '').split(',')
    post_ids = [int(i) for i in raw_ids if i.isdigit()]
    
    last_check_raw = request.GET.get('last_check')
    last_check = parse_datetime(last_check_raw) if last_check_raw else None
    
    data = {
        'stats': {},
        'new_replies': {},
        'new_posts_count': 0, 
    }

    if not post_ids or not last_check:
        return JsonResponse(data)

    replies_filter = models.Reply.objects.filter(created_at__gt=last_check).select_related('user')
    
    # Если юзер авторизован, исключаем его комменты (чтобы он не получал уведомление о своем же комменте)
    if request.user.is_authenticated:
        replies_filter = replies_filter.exclude(user=request.user)

    posts = models.Post.objects.filter(id__in=post_ids).annotate(
        l_count=Count('likes', distinct=True),
        r_count=Count('replies', distinct=True)
    ).prefetch_related(
    Prefetch('replies', queryset=models.Reply.objects.all(), to_attr='all_replies_cached'),
    Prefetch('replies', queryset=replies_filter, to_attr='new_only')
    )

    for post in posts:
        # Теперь все данные уже в памяти!
        data['stats'][post.id] = {
            'likes': post.l_count, 
            'replies': post.r_count,
            # Используем list comprehension, чтобы не лезть в базу
            'active_replies': [r.id for r in post.all_replies_cached],
            'created_at': post.created_at.strftime('%d.%m')
        }
        
        # Если в памяти есть новые комменты — рендерим
        if post.new_only:
            data['new_replies'][post.id] = render_to_string(
                'posts/includes/replies_ajax.html',
                {'replies': post.new_only, 'user': request.user, 'post': post},
                request=request
            )
            
    return JsonResponse(data)
