from django.db import models
from django.contrib.auth.models import AbstractUser

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

    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, null=True, blank=True)
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
            
        # Если это админ — проверяем, разрешено ли админам здесь хозяйничать
        if getattr(user, 'is_admin', False) and allow_admin:
            return True
            
        return False
    
class Post(models.Model):
    name = models.CharField(max_length=40)
    about = models.TextField()
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
        