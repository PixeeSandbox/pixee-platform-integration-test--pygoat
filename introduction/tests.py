import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_nslookup_without_shell_for_windows_branch(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'nslookup output', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_dig_without_shell_for_non_windows_branch(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'dig output', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_subprocess_execution(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(response.context['output'], 'Something went wrong')
