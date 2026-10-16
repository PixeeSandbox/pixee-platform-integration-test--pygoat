from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='dummyuser',
            password='password123',
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_normal_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'ok', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=-1,
            stderr=-1,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_passes_shell_metacharacters_as_single_argument(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'ok', b'')
        mock_popen.return_value = process

        malicious_domain = 'example.com; rm -rf /'
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': malicious_domain, 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', malicious_domain],
            shell=False,
            stdout=-1,
            stderr=-1,
        )
