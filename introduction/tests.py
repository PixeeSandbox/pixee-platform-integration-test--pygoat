from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='security_tester', password='Password123!')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_invokes_subprocess_with_argument_list(self, mock_run):
        mock_run.return_value.stdout = 'lookup ok'
        mock_run.return_value.stderr = ''

        response = self.client.post(self.url, {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, check=False)
        self.assertNotIn('shell', mock_run.call_args.kwargs)
        self.assertIn('lookup ok', response.content.decode())
