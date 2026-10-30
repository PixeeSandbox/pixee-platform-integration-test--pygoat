import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings


@override_settings(ALLOWED_HOSTS=['testserver'])
class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmdlab3user', password='password123')
        self.assertTrue(self.client.login(username='cmdlab3user', password='password123'))

    def test_cmd_lab3_rejects_malicious_domain_before_shell_execution(self):
        with patch('introduction.other_views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com && id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'uid=')
        mocked_popen.assert_not_called()

    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self):
        class FakeProcess:
            def communicate(self):
                return (b'lookup ok\n', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=FakeProcess()) as mocked_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mocked_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
