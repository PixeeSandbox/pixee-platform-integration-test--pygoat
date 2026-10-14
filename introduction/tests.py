from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client_user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123",
        )
        self.url = reverse('Command Injection Lab 3')

    def test_unauthenticated_requests_redirect_to_login(self):
        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={self.url}")

    @patch('introduction.other_views.subprocess.Popen')
    def test_authenticated_malicious_domain_is_rejected_safely(self, mock_popen):
        self.client.force_login(self.client_user)

        response = self.client.post(
            self.url,
            {'domain': 'https://www.example.com;id', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
