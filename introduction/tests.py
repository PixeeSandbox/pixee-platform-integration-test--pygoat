from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3-user',
            password='password12345',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_executes_valid_domain_without_shell(self, mock_run, mock_render):
        mock_run.return_value = Mock(stdout='resolved\n', stderr='')
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotIn('shell', mock_run.call_args.kwargs)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'resolved\n'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_injection_payload(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('blocked')

        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com; whoami', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
