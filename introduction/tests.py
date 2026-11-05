from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertTrue(self.client.login(username='testuser', password='testpass123'))
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_run):
        mock_run.return_value.stdout = 'resolved\n'
        mock_run.return_value.stderr = ''
        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', 'example.com'], shell=False, capture_output=True, text=True)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters_before_subprocess_execution(self, mock_run):
        response = self.client.post(self.url, {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
