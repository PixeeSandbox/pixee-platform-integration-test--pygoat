import subprocess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _build_request(self, data):
        request = self.factory.post('/cmd_lab/', data=data)
        request.user = self.user
        return request

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell_for_benign_domain(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context=None, **kwargs: HttpResponse(context['output'])

        request = self._build_request({'domain': 'https://www.example.com', 'os': 'win'})
        response = cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(response.content, b'lookup output')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context=None, **kwargs: HttpResponse(context['output'])

        request = self._build_request({'domain': 'example.com; cat /etc/passwd', 'os': 'linux'})
        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertEqual(response.content, b'Something went wrong')
