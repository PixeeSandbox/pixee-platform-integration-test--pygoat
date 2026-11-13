import subprocess
from unittest.mock import call, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_command_injection_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_unsupported_os(self, mock_popen):
        self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'mac',
        })

        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_supported_executables_and_separate_hostname_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab', {
            'domain': 'www.example.com',
            'os': 'linux',
        })
        self.client.post('/cmd_lab', {
            'domain': 'www.example.com',
            'os': 'win',
        })

        self.assertEqual(mock_popen.call_args_list, [
            call(['dig', 'www.example.com'], shell=False,
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(['nslookup', 'www.example.com'], shell=False,
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE),
        ])
