from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUsers(AbstractUser):
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
        return self.role == self.ROLE_ADMIN
    
class Posts(models.Model):
    name = models.CharField(max_length=40)
    about = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(CustomUsers, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
