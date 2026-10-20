from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
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
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = Mock()
        request = self.factory.post(
            '/cmd_lab3/',
            data={'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
        self.assertEqual(response, mock_render.return_value)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process
        mock_render.return_value = Mock()
        request = self.factory.post(
            '/cmd_lab3/',
            data={'domain': 'example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'example output'},
        )
