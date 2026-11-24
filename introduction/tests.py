from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLab3CommandInjectionTest(TestCase):
    def test_rejects_shell_syntax_without_running_command(self):
        user = get_user_model().objects.create_user(username='cmdtest', password='test-password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post(
                reverse('Command Injection Lab 3'),
                {'domain': 'example.com; touch /tmp/command-injection', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
