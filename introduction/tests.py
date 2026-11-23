from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLab3Tests(TestCase):
    def test_rejects_hostname_with_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as process:
            response = self.client.post(
                reverse('Command Injection Lab 3'),
                {'domain': 'example.com; whoami', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 400)
        process.assert_not_called()
