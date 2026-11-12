import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_separate_argument(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        for os_value, executable in [('win', 'nslookup'), ('linux', 'dig')]:
            with self.subTest(os=os_value):
                mock_popen.reset_mock()
                response = self.client.post('/cmd_lab', {'domain': 'a.example.com', 'os': os_value})

                self.assertEqual(response.status_code, 200)
                mock_popen.assert_called_once_with(
                    [executable, 'a.example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

    @patch('introduction.views.subprocess.Popen')
    def test_invalid_domain_is_rejected_without_subprocess(self, mock_popen):
        for domain in ('example.com; whoami', '-invalid.example', 'bad..example'):
            with self.subTest(domain=domain):
                response = self.client.post('/cmd_lab', {'domain': domain, 'os': 'win'})

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
