import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    def test_valid_hostname_uses_fixed_executable_and_argument(self):
        for os_selection, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_selection):
                with patch('introduction.views.subprocess.Popen') as popen:
                    popen.return_value.communicate.return_value = (b'lookup output', b'')
                    response = self.client.post('/cmd_lab', {'domain': 'www.example.com', 'os': os_selection})

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, 'www.example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
