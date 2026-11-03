import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab3/', {
            'domain': 'example.com; id',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertIn('Something went wrong', response.content.decode())

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_both_os_branches(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        for os_value, expected_command in (
            ('win', ['nslookup', 'example.com']),
            ('linux', ['dig', 'example.com']),
        ):
            request = self.factory.post('/cmd_lab3/', {
                'domain': 'https://www.example.com',
                'os': os_value,
            })
            request.user = self.user

            response = cmd_lab3(request)

            self.assertEqual(response.status_code, 200)
            args, kwargs = mock_popen.call_args
            self.assertEqual(args[0], expected_command)
            self.assertFalse(kwargs.get('shell', False))
            self.assertEqual(kwargs['stdout'], subprocess.PIPE)
            self.assertEqual(kwargs['stderr'], subprocess.PIPE)
            mock_popen.reset_mock()
