from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com; whoami', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_subprocess_arguments_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = ('safe output', '')
        mock_popen.return_value = process

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'safe output')
        mock_popen.assert_called_once()
        call_args, call_kwargs = mock_popen.call_args
        self.assertEqual(call_args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', call_kwargs)
