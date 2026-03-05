from django.test import TestCase
from .models import Post
class PostLstTest(TestCase):
    def test_post_list_access(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_api_post_list(self):
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        post = Post.objects.create(
            name = "ggg",
            about = "jjj"
        )
        self.assertEqual(post.name, "ggg")
        self.assertEqual(post.about, "jjj")
