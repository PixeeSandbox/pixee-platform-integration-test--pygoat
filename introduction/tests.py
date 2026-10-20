from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest import mock


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @mock.patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen):
        process_mock = mock.Mock()
        process_mock.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process_mock

        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'example output', response.content)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))

    @mock.patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injected_domain_before_subprocess(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com;id', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()
