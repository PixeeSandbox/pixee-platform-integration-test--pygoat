from django.test import TestCase, RequestFactory
from unittest.mock import ANY, Mock, patch
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123'
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rendered')
        request = self.factory.post('/cmd_lab3/', {
            'domain': 'https://www.example.com; rm -rf /',
            'os': 'win'
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('rendered')
        request = self.factory.post('/cmd_lab3/', {
            'domain': 'https://www.example.com',
            'os': 'win'
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))
        self.assertEqual(response.status_code, 200)
