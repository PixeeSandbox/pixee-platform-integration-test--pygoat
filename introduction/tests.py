import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdtester',
            password='StrongPass123!',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_command_execution(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com; id', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false_for_valid_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'answer', b'')
        mock_popen.return_value = process

        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
