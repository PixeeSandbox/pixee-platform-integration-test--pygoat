import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd-user',
            password='testpass123',
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'nslookup output', b'')
        mock_render.return_value = None

        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = None

        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'https://www.example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(
            mock_render.call_args[0][2]['output'],
            'Invalid domain provided',
        )
