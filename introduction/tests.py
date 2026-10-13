import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, data):
        request = self.factory.post('/cmd_lab/', data=data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_valid_domain_uses_safe_subprocess_arguments(self, mock_run, mock_popen, mock_render):
        mock_run.return_value = SimpleNamespace(stdout=b'ok', stderr=b'')
        mock_render.return_value = HttpResponse('rendered')

        request = self._authenticated_post({'domain': 'https://www.example.com', 'os': 'win'})
        response = cmd_lab(request)

        self.assertEqual(response.content, b'rendered')
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        args, kwargs = mock_render.call_args
        self.assertEqual(args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(args[2], {'output': 'ok'})

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_shell_metacharacters_without_subprocess(self, mock_run, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('invalid')

        request = self._authenticated_post({'domain': 'example.com; rm -rf /', 'os': 'linux'})
        response = cmd_lab(request)

        self.assertEqual(response.content, b'invalid')
        mock_run.assert_not_called()
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        args, kwargs = mock_render.call_args
        self.assertEqual(args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(args[2], {'output': 'Something went wrong'})
