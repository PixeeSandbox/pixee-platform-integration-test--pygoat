from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch

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
    def test_windows_branch_uses_nslookup_argv(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'nslookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell'))
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'nslookup output')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_non_windows_branch_uses_dig_argv(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'dig output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell'))
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'dig output')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_invalid_domain_rejected_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Something went wrong')
