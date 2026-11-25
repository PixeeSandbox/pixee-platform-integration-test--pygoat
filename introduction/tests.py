from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def test_rejects_domain_with_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post(
                reverse('Command Injection Lab 3'),
                {'domain': 'example.com; whoami', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
