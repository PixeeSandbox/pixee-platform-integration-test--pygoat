import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters_without_starting_process(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_passes_valid_hostname_as_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post('/cmd_lab', {'domain': 'www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
