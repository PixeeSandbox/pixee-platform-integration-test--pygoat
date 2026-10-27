from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_valid_domain_uses_argument_list_and_returns_combined_output(self, mock_run):
        mock_run.return_value.stdout = 'stdout output\n'
        mock_run.return_value.stderr = 'stderr output\n'

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.Example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, check=False)
        self.assertContains(response, 'stdout output')
        self.assertContains(response, 'stderr output')

    @patch('introduction.other_views.subprocess.run')
    def test_malicious_domain_is_rejected_before_subprocess_call(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Invalid domain supplied')
