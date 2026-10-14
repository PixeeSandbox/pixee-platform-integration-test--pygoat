import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_request(self, domain, os_value='linux'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    def test_rejects_injected_domain_before_command_execution(self):
        request = self._build_request('example.com;id')

        with patch('introduction.other_views.render', return_value=HttpResponse('rendered')) as mock_render, \
                patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Invalid domain')
        self.assertEqual(response.status_code, 200)

    def test_uses_argument_list_and_shell_false_for_valid_domain(self):
        request = self._build_request('example.com')
        process = SimpleNamespace(communicate=lambda: (b'output', b''))

        with patch('introduction.other_views.render', return_value=HttpResponse('rendered')) as mock_render, \
                patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
