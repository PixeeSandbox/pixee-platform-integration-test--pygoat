from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3CommandInjectionTest(TestCase):
    def test_rejects_hostname_with_shell_metacharacter(self):
        user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
