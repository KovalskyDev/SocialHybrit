from rest_framework.generics import ListAPIView, ListCreateAPIView
from MainPage import models
from .serializers import PostSerializer


class PostListAPI(ListAPIView):
    """
    ### API Список Постов
    Этот эндпоинт возвращает список всех публикаций в соцсети.
    
    **Доступные данные:**
    * `likers_ages` — список возрастов всех пользователей, поставивших лайк.
    * `average_liker_age` — средний возраст аудитории данного поста.
    
    *Примечание: данные обновляются в реальном времени.*
    """
    queryset = models.Post.objects.prefetch_related('likes__user').all()
    serializer_class = PostSerializer
