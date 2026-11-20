from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3CommandInjectionTest(TestCase):
    def test_rejects_domain_with_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='cmd_lab3_test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                reverse('Command Injection Lab 3'),
                {'domain': 'example.com;whoami', 'os': 'linux'},
            )

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
