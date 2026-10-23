from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            email='cmdlabuser@example.com',
            password='StrongPass123!',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_accepts_dns_safe_domain(self, mock_run):
        mock_run.return_value.stdout = 'resolved output\n'
        mock_run.return_value.stderr = ''

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved output')
        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()
