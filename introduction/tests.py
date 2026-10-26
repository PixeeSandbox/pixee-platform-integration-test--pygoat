import subprocess
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen_mock, patch('introduction.other_views.render') as render_mock:
            render_mock.return_value = HttpResponse('ok')

            response = cmd_lab3(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]['output'], 'Invalid domain')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')

    def test_cmd_lab3_uses_argv_list_without_shell_for_valid_domain(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        process = SimpleNamespace(communicate=lambda: (b'valid', b''))

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen_mock, patch('introduction.other_views.render') as render_mock:
            render_mock.return_value = HttpResponse('ok')

            response = cmd_lab3(request)

        popen_mock.assert_called_once()
        self.assertEqual(popen_mock.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(popen_mock.call_args.kwargs['shell'])
        self.assertEqual(popen_mock.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(popen_mock.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')
