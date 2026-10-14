from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_selects_nslookup_on_win_and_dig_otherwise(self, mock_popen):
        self.client.force_login(self.user)
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'lookup output', b'')

        self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])

        mock_popen.reset_mock()
        self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injected_domain_before_command_execution(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
