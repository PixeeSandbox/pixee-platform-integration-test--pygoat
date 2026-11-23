import subprocess
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.render', return_value=HttpResponse())
    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.render', return_value=HttpResponse())
    @patch('introduction.views.subprocess.Popen')
    def test_hostname_with_shell_metacharacters_is_rejected(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()

        cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
