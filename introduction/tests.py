from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.login(username='testuser', password='testpass123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_before_command_execution(self, popen_mock):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {
                'domain': 'example.com;id',
                'os': 'linux',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        popen_mock.assert_not_called()
