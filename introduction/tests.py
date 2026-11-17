import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    def test_invalid_domains_are_rejected_without_launching_subprocess(self):
        for domain in ('example.com; whoami', '-invalid.example', 'a' * 64 + '.com'):
            with self.subTest(domain=domain):
                with patch('introduction.other_views.subprocess.Popen') as popen:
                    response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'linux'})

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Invalid domain')
                popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
