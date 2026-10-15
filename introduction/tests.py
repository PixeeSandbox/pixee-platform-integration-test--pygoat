from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_and_shell_false(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'lookup output'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid input'})
