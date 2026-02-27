from rest_framework.generics import ListAPIView, ListCreateAPIView
from MainPage import models
from .serializers import PostSerializer


class PostListAPI(ListAPIView):
    queryset = models.Post.objects.prefetch_related('likes__user').all()
    serializer_class = PostSerializer
