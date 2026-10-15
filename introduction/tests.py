from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_allows_valid_hostname(self, mock_run):
        mock_run.return_value.stdout = 'example.com name server response'
        mock_run.return_value.stderr = ''

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_hostname(self, mock_run):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com; id', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 400)
        mock_run.assert_not_called()
