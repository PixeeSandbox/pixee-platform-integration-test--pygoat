import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_invokes_lookup_safely_for_valid_domain(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
