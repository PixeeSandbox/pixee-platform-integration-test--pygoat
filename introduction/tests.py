import subprocess

from django.test import TestCase, RequestFactory
from django.http import HttpResponse, HttpResponseBadRequest
from types import SimpleNamespace
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        mock_popen.return_value.communicate.return_value = (b'example output', b'')
        mock_render.return_value = HttpResponse('rendered')

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertEqual(kwargs['shell'], False)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'rendered')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_invalid_domain_returns_bad_request(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'bad;rm -rf /', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
        mock_render.assert_not_called()
