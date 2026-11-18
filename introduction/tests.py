import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_command_injection_domain_is_rejected_without_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        for operating_system, executable in [('win', 'nslookup'), ('linux', 'dig')]:
            with self.subTest(operating_system=operating_system):
                response = self.client.post('/cmd_lab', {
                    'domain': 'https://www.example.com',
                    'os': operating_system,
                })

                self.assertEqual(response.status_code, 200)
                mock_popen.assert_called_with(
                    [executable, 'example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
