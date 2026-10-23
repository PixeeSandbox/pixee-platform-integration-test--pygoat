import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com;whoami', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com;whoami'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'lookup output')
