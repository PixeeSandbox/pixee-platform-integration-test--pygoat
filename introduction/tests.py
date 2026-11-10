import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_injection_payload(self, popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_uses_fixed_executable_and_separate_hostname_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.context['output'], 'lookup output')
