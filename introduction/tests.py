from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionRegressionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='command-test', password='test-password')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_runs_fixed_command_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(self.url, {'domain': 'www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'www.example.com'])
        self.assertIs(kwargs['shell'], False)

    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_hostname_is_rejected(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
