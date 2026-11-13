import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_syntax_without_spawning_subprocess(self, popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_argument_list(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
