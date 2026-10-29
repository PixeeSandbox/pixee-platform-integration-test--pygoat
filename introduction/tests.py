import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'google.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_allows_normal_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'Lookup OK', b'')

        response = self.client.post('/cmd_lab', {'domain': 'google.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lookup OK')
        mock_popen.assert_called_once_with(
            ['dig', 'google.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
