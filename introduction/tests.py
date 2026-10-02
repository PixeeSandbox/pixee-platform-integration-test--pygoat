import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'example output'},
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_popen(self, mock_popen, mock_render):
        mock_render.return_value = Mock()

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
