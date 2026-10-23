from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlabuser', password='StrongPass123!')
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_valid_domain_uses_safe_argument_list(self, mock_run):
        mock_run.return_value.stdout = 'resolved output\n'
        mock_run.return_value.stderr = ''

        logged_in = self.client.login(username='cmdlabuser', password='StrongPass123!')
        self.assertTrue(logged_in)

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved output')
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_invalid_domain_without_invoking_subprocess(self, mock_run):
        logged_in = self.client.login(username='cmdlabuser', password='StrongPass123!')
        self.assertTrue(logged_in)

        response = self.client.post(self.url, {'domain': 'example.com; id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()
