import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, popen_mock, render_mock):
        request = self.factory.post(
            '/cmd_lab3/',
            data={'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = SimpleNamespace(is_authenticated=True)
        render_mock.return_value = 'rendered-response'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered-response')
        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_argument_list(self, popen_mock, render_mock):
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b'lookup output', b'')
        popen_mock.return_value = process_mock
        request = self.factory.post(
            '/cmd_lab3/',
            data={'domain': 'https://www.Example.com', 'os': 'win'},
        )
        request.user = SimpleNamespace(is_authenticated=True)
        render_mock.return_value = 'rendered-response'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered-response')
        popen_mock.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookup output'},
        )
