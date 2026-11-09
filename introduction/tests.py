from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='password123')

    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self):
        self.client.login(username='alice', password='password123')

        with patch('introduction.other_views.subprocess.run') as mock_run:
            mock_run.return_value.stdout = 'resolved output'
            mock_run.return_value.stderr = ''

            response = self.client.post('/cmd_lab3', {'domain': 'Example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', 'example.com'], shell=False, capture_output=True, text=True, check=False)
        self.assertContains(response, 'resolved output')

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        self.client.login(username='alice', password='password123')

        with patch('introduction.other_views.subprocess.run') as mock_run:
            response = self.client.post('/cmd_lab3', {'domain': '-example.com && whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Invalid domain')
