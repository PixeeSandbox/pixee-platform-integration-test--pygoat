import subprocess

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_and_shell_false(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'ok\n', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': ' https://www.example.com ',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertContains(response, 'ok')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injected_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
