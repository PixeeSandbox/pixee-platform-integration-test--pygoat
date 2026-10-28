import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_renders_output(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid stdout\n', b'valid stderr\n')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid stdout')
        self.assertContains(response, 'valid stderr')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_malicious_domain_is_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; cat /etc/passwd',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
