from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def test_rejects_shell_metacharacters_in_domain(self):
        user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mocked_popen:
            response = self.client.post(reverse('Command Injection Lab 3'), {
                'domain': 'example.com;id',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 400)
        mocked_popen.assert_not_called()
