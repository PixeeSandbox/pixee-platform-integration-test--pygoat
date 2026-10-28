from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
import subprocess


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_uses_argv_without_shell(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)
        domain = 'https://www.example.com; rm -rf /'

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'fake stdout', b'fake stderr')

            response = self.client.post(reverse('Command Injection Lab 3'), {
                'domain': domain,
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; rm -rf /'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
