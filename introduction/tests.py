import subprocess
from unittest.mock import call, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_fixed_command(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        for os_choice, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_choice):
                response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': os_choice})

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    mock_popen.call_args,
                    call(
                        [executable, 'example.com'],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    ),
                )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_injection_domains(self, mock_popen):
        payloads = (
            'example.com;whoami',
            'example.com&&whoami',
            'example.com|whoami',
            'example.com\nwhoami',
        )

        for domain in payloads:
            with self.subTest(domain=domain):
                response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'win'})

                self.assertEqual(response.status_code, 400)
                mock_popen.assert_not_called()
