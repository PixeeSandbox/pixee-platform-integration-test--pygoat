from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_allows_valid_hostname(self, mock_run):
        mock_run.return_value.stdout = 'mock lookup output'
        mock_run.return_value.stderr = ''
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('mock lookup output', response.content.decode())
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
        )
