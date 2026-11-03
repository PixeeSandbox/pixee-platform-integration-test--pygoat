from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import ANY, MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_safe_domain_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = MagicMock()

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = MagicMock()

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;whoami', 'os': 'win'})
        request.user = self.user

        cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
