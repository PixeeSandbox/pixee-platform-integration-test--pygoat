from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_hostname_uses_argv_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'valid', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_execution(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content.decode(), 'Something went wrong')
        mock_popen.assert_not_called()
