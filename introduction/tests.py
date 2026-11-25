import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_running_process(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_runs_fixed_executable_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'lookup output')
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
