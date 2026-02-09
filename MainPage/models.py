from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUsers(AbstractUser):
    GENDER_FEMALE = "female"
    GENDER_MALE = "male"

    GENDER_CHOICES = [
        (GENDER_MALE, "Чоловік"),
        (GENDER_FEMALE, "Жінка")
    ]

    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"
        ordering = ["id"]

    def __str__(self):
        return self.username
    
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

