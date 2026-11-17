from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post_request(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render', return_value=HttpResponse())
    def test_rejects_shell_syntax_in_domain(self, mock_render, mock_popen):
        from introduction.other_views import cmd_lab3

        response = cmd_lab3(self._post_request({'domain': 'example.com; whoami', 'os': 'win'}))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render', return_value=HttpResponse())
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_render, mock_popen):
        from introduction.other_views import cmd_lab3
        import subprocess

        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')
        response = cmd_lab3(self._post_request({'domain': 'www.example.com', 'os': 'win'}))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
