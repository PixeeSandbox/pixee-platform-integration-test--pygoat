import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlabuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_linux_uses_dig_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'linux output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; rm -rf /'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_windows_uses_nslookup_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'windows output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com && calc', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com && calc'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
