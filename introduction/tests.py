from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_and_no_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'good output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com ', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args[1].get('shell'))
        self.assertEqual(mock_render.call_args[0][2]['output'], 'good output')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Something went wrong')
