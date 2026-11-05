from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from unittest.mock import patch, MagicMock

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def _make_request(self, domain, os_value='linux'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self._make_request('example.com;whoami')
        with patch('introduction.other_views.render', side_effect=lambda req, tpl, ctx: HttpResponse(ctx['output'])), \
                patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.content.decode(), 'Invalid domain')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self._make_request('example.com')
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        with patch('introduction.other_views.render', side_effect=lambda req, tpl, ctx: HttpResponse(ctx['output'])), \
                patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.content.decode(), 'output')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell'))
