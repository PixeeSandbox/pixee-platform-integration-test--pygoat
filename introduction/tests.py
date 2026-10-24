from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password12345')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post(self.url, {'domain': 'example.com;id', 'os': 'linux'})

        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout='lookup output', stderr='')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True)
        self.assertNotIn('shell', mock_run.call_args.kwargs)
        self.assertContains(response, 'lookup output')
