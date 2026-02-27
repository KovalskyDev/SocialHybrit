from django.db.models import Avg # Импортируем агрегацию
from rest_framework import serializers
from MainPage import models

class PostSerializer(serializers.ModelSerializer):
    likers_ages = serializers.SerializerMethodField()
    average_liker_age = serializers.SerializerMethodField()

    class Meta:
        model = models.Post
        fields = [
            "name", "created_at", "likes_count", 
            "replies_count", "likers_ages", "average_liker_age"
        ]

    def get_likers_ages(self, obj):
        # Твой код, только чуть лаконичнее
        ages = obj.likes.values_list('user__age', flat=True)
        return list(ages) if ages.exists() else []

    def get_average_liker_age(self, obj):
        # Агрегация на уровне БД. Вернет среднее по полю 'user__age'
        result = obj.likes.aggregate(Avg('user__age'))['user__age__avg']
        # Округлим до одного знака после запятой, если не None
        return round(result) if result is not None else 0