import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdtester',
            password='strong-password-123',
        )

    def _build_request(self, data):
        request = self.factory.post('/cmd_lab/', data)
        request.user = self.user
        return request

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'resolved\n', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(
            (context or {}).get('output', '')
        )

        request = self._build_request({'domain': 'https://www.example.com', 'os': 'linux'})
        response = cmd_lab(request)

        self.assertEqual(response.content.decode(), 'resolved\n')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertEqual(mock_popen.call_args.kwargs.get('stdout'), subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs.get('stderr'), subprocess.PIPE)
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(
            (context or {}).get('output', '')
        )

        request = self._build_request({'domain': 'example.com; rm -rf /', 'os': 'linux'})
        response = cmd_lab(request)

        self.assertIn('Invalid domain', response.content.decode())
        mock_popen.assert_not_called()
