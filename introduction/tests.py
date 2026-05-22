import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import _validate_cmd_domain, cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_validate_cmd_domain_accepts_localhost_and_fqdn(self):
        self.assertEqual(_validate_cmd_domain('localhost'), 'localhost')
        self.assertEqual(_validate_cmd_domain('https://www.example.com/'), 'example.com')

    def test_validate_cmd_domain_rejects_invalid_values(self):
        for value in ['', None, 'example.com; rm -rf /', 'bad host', 'example.com|whoami']:
            with self.assertRaises(ValueError):
                _validate_cmd_domain(value)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab', {'domain': 'localhost', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'localhost'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injected_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2], {'output': 'Something went wrong'})
