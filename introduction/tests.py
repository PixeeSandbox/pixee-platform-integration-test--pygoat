import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    @patch('introduction.other_views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'stdout', b'stderr')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'stdoutstderr'}
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))

    @patch('introduction.other_views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected_before_command_execution(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
