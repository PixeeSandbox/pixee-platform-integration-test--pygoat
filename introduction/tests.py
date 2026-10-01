import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, domain, os_value):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    def _fake_render(self, request, template_name, context=None, *args, **kwargs):
        response = HttpResponse('rendered')
        response.context_data = context or {}
        response.template_name = template_name
        return response

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')
        mock_render.side_effect = self._fake_render

        request = self._authenticated_post('https://www.example.com', 'win')
        response = cmd_lab(request)

        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(response.context_data['output'], 'lookup ok')
        self.assertEqual(response.template_name, 'Lab/CMD/cmd_lab.html')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_malicious_domain_is_rejected_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = self._fake_render

        request = self._authenticated_post('https://www.example.com; rm -rf /', 'linux')
        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.context_data['output'], 'Something went wrong')
        self.assertEqual(response.template_name, 'Lab/CMD/cmd_lab.html')
