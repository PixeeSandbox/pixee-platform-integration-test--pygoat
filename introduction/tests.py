import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='cmdlabuser',
            email='cmdlabuser@example.com',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_dig(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'dig output', b'')
        mock_popen.return_value = process

        domain = 'example.com;whoami'
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': domain, 'os': 'linux'},
        )

        mock_popen.assert_called_once_with(
            ['dig', domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dig output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_nslookup(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'nslookup output', b'')
        mock_popen.return_value = process

        domain = 'example.com && echo pwned'
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': domain, 'os': 'win'},
        )

        mock_popen.assert_called_once_with(
            ['nslookup', domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'nslookup output')
