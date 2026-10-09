import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_non_win(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        payload = 'example.com; id'
        response = self.client.post('/cmd_lab3', {'domain': payload, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(['dig', payload], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_win(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        payload = 'example.com; id'
        response = self.client.post('/cmd_lab3', {'domain': payload, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(['nslookup', payload], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
