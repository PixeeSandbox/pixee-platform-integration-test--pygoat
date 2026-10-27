from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;rm -rf /', 'os': 'linux'})
        request.user = self.user
        mock_render.return_value = HttpResponse('rendered')

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'ok', b'')
        mock_render.return_value = HttpResponse('rendered')

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        mock_render.assert_called_once()
