import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_injection_domain(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    def test_valid_domains_use_fixed_executable_and_argument_list(self):
        for os_option, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_option), patch('introduction.views.subprocess.Popen') as popen:
                popen.return_value.communicate.return_value = (b'', b'')
                response = self.client.post('/cmd_lab', {'domain': 'www.example.com', 'os': os_option})

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, 'www.example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
