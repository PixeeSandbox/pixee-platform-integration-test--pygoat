from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123'
        )

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render')
    def test_cmd_lab3_uses_argument_vector(self, mock_render, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.assertEqual(response.status_code, 200)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
