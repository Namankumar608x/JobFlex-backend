from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class UpdateProfileLinksAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            email="test@example.com",
            uname="tester",
        )
        self.user.set_password("password123")
        self.user.save()

    def test_update_profile_links_updates_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/user/update-profile-links/",
            {
                "linkedin_url": "https://www.linkedin.com/in/tester",
                "leetcode_username": "leet_tester",
                "codeforces_username": "cf_tester",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(
            self.user.linkedin_url,
            "https://www.linkedin.com/in/tester",
        )
        self.assertEqual(self.user.Leetcode_username, "leet_tester")
        self.assertEqual(self.user.Codeforces_username, "cf_tester")

    def test_update_profile_links_requires_authentication(self):
        response = self.client.post(
            "/user/update-profile-links/",
            {"linkedin_url": "https://www.linkedin.com/in/tester"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
