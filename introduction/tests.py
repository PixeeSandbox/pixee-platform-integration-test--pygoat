import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab3(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab3(request)

    @patch('introduction.other_views.render', return_value=HttpResponse())
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_syntax_without_starting_subprocess(self, mock_popen, mock_render):
        self.post_cmd_lab3({'domain': 'example.com;whoami', 'os': 'win'})

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(
            mock_render.call_args[0][1:],
            ('Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'}),
        )

    @patch('introduction.other_views.render', return_value=HttpResponse())
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_runs_fixed_utility_without_a_shell(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post_cmd_lab3({'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
