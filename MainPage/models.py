from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    GENDER_FEMALE = "female"
    GENDER_MALE = "male"

    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female")
    ]

    ROLE_ADMIN = "admin"
    ROLE_USER = "user"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrator"),
        (ROLE_USER, "User")
    ]

    age = models.PositiveIntegerField(null=True, blank=True, validators=[
            MinValueValidator(13, message="Тобі має бути хоча б 13 років!"),
            MaxValueValidator(100, message="Ну ти і довгожитель. Введи реальний вік!")
        ])
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_USER)

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"
        ordering = ["id"]

    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором через поле role."""
        return self.role == self.ROLE_ADMIN
    
    def can_manage(self, user, allow_admin=True):
        """
        Проверяет, может ли конкретный юзер управлять этим постом.
        """
        if not user or user.is_anonymous:
            return False
        # Если это сам владелец профиля — всегда можно
        if self == user:
            return True
        # Если это админ — проверяем, разрешено ли админам здесь управлять
        if getattr(user, 'is_admin', False) and allow_admin:
            return True
            
        return False
    
class Post(models.Model):
    name = models.CharField(max_length=100)
    about = models.TextField(max_length=2200)
    media = models.FileField(upload_to="post_media/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="posts")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
    
    def can_manage(self, user, allow_admin=True):
        """
        Проверяет, может ли конкретный юзер управлять этим постом.
        """
        if not user or user.is_anonymous:
            return False
        
        # Если это сам владелец профиля — всегда можно
        if self.creator == user:
            return True
            
        # Если это админ — проверяем, разрешено ли админам здесь хозяйничать
        if getattr(user, 'is_admin', False) and allow_admin:
            return True
            
        return False
    
    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def replies_count(self):
        return self.replies.count()

    def save(self, *args, **kwargs):
        if self.about:
            self.about = self.about.strip() # Удалит пробелы и переносы в начале и конце
        super().save(*args, **kwargs)

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        verbose_name = "Like"
        verbose_name_plural = "Likes"
    
    def __str__(self):
        return f"{self.user.username} likes post {self.post.name}"
    
class Reply(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_replies")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="replies")
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at'] # Старые сверху, новые добавляются вниз

    def __str__(self):
        return f"{self.user.username} до {self.post.name[:20]}"