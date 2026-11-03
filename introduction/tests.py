from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _build_request(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    def test_cmd_lab3_valid_domain_uses_argv_list(self):
        request = self._build_request('example.com')
        with patch('introduction.other_views.subprocess.run') as mock_run, patch('introduction.other_views.render') as mock_render:
            mock_run.return_value = SimpleNamespace(stdout=b'lookup ok', stderr=b'')
            mock_render.return_value = HttpResponse('rendered')

            response = cmd_lab3(request)

        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_run.call_args.kwargs)
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'lookup ok')
        self.assertEqual(response.content, b'rendered')

    def test_cmd_lab3_rejects_domain_with_command_separator(self):
        request = self._build_request('example.com;whoami')
        with patch('introduction.other_views.subprocess.run') as mock_run, patch('introduction.other_views.render') as mock_render:
            mock_render.return_value = HttpResponse('Invalid domain')

            response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Invalid domain')
        self.assertEqual(response.content, b'Invalid domain')

    def test_cmd_lab3_rejects_option_like_domain(self):
        request = self._build_request('-example.com')
        with patch('introduction.other_views.subprocess.run') as mock_run, patch('introduction.other_views.render') as mock_render:
            mock_render.return_value = HttpResponse('Invalid domain')

            response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Invalid domain')
        self.assertEqual(response.content, b'Invalid domain')
