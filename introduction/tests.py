import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLookupTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_argv(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_windows_uses_nslookup(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertIs(popen.call_args.kwargs['shell'], False)

    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected(self, popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
