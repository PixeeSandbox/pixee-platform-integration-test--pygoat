from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_subprocess_invocation(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'https://www.Example.COM.', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertContains(response, 'lookup ok')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
