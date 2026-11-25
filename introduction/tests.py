import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_hostname_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        for os_value, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_value):
                response = self.client.post('/cmd_lab3', {
                    'domain': 'www.example.com',
                    'os': os_value,
                })

                self.assertEqual(response.status_code, 200)
                mock_popen.assert_called_with(
                    [executable, 'www.example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_invalid_hostname_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
