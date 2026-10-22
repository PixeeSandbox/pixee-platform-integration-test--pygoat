from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_benign_domain(self, mock_run):
        mock_run.return_value = Mock(stdout='lookup output\n', stderr='')

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertContains(response, 'lookup output')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain supplied')
        mock_run.assert_not_called()
