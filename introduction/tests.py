from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='testpass123'
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_valid_post_uses_argv_and_returns_output(self, mock_run):
        mock_run.return_value.stdout = 'lookup ok\n'
        mock_run.return_value.stderr = ''
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)
        self.assertIn('lookup ok', response.content.decode())

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertFalse(mock_run.called)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())
