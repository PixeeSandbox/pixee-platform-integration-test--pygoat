from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters_in_domain(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com; touch /tmp/injected', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid input')
        popen.assert_not_called()
