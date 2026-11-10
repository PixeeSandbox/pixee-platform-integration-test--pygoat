import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_runs_valid_domain_without_shell(self, popen):
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
