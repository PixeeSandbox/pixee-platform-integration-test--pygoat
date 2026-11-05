from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import Mock, patch
import subprocess


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_valid_domain_uses_argument_list_and_renders_output(self, mock_run):
        mock_run.return_value = Mock(stdout='resolved\n', stderr='')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved')
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)

    @patch('introduction.other_views.subprocess.run')
    def test_malicious_domain_is_rejected_without_subprocess_call(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain provided')
        mock_run.assert_not_called()
