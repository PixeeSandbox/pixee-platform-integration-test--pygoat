import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'ok', b'')
        mock_render.return_value = 'rendered'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'ok'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user
        mock_render.return_value = 'rendered'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )

    def test_cmd_lab3_anonymous_user_redirects_to_login(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = AnonymousUser()

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 302)
