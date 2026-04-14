from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from blog.models import Blog, Comment, Upvote
from user.models import User


@override_settings(DEBUG=True)
class BlogApiPerformanceTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.author = User.objects.create(
            email="author@example.com",
            uname="author",
        )
        self.author.set_password("password123")
        self.author.save(update_fields=["password"])

        self.commenter = User.objects.create(
            email="commenter@example.com",
            uname="commenter",
        )
        self.commenter.set_password("password123")
        self.commenter.save(update_fields=["password"])

        self.blogs = [
            Blog.objects.create(
                U_ID=self.author,
                title=f"Blog {index}",
                blogtext=f"Body {index}",
            )
            for index in range(3)
        ]

        for blog in self.blogs:
            Comment.objects.create(
                blog=blog,
                U_ID=self.commenter,
                comment_text=f"Comment for {blog.title}",
            )
            Upvote.objects.create(blog=blog, U_ID=self.commenter)

        self.blog_list_url = "/api/blogs/"

    def test_blog_list_uses_optimized_query_count(self):
        with self.assertNumQueries(2):
            response = self.client.get(self.blog_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["uname"], "author")
        self.assertEqual(response.data[0]["comments"][0]["uname"], "commenter")
        self.assertEqual(response.data[0]["upvote_count"], 1)

    def test_blog_detail_uses_optimized_query_count(self):
        with self.assertNumQueries(2):
            response = self.client.get(f"{self.blog_list_url}{self.blogs[0].pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uname"], "author")
        self.assertEqual(response.data["comments"][0]["uname"], "commenter")
        self.assertEqual(response.data["upvote_count"], 1)
