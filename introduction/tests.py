import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='safe-password-123',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com; id', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'answer\n', b'')
        mock_popen.return_value = process

        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertIs(kwargs['stdout'], subprocess.PIPE)
        self.assertIs(kwargs['stderr'], subprocess.PIPE)
        self.assertContains(response, 'answer')
