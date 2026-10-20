from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    @patch('introduction.other_views.render', return_value=HttpResponse('invalid'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab3',
            {
                'domain': 'example.com; rm -rf /',
                'os': 'win',
            },
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.content, b'invalid')

    @patch('introduction.other_views.render', return_value=HttpResponse('valid'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argument_list_without_shell_for_valid_domain(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab3',
            {
                'domain': 'https://www.example.com',
                'os': 'win',
            },
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(response.content, b'valid')
