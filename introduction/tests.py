import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_accepts_valid_hostname_with_non_shell_subprocess(self, popen_mock, render_mock):
        process_mock = SimpleNamespace(communicate=lambda: (b'1.2.3.4\n', b''))
        popen_mock.return_value = process_mock
        render_mock.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': '1.2.3.4\n'},
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injected_hostname_before_subprocess(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; id', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
