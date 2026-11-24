from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    @patch('introduction.other_views.subprocess.Popen')
    def test_invalid_domain_does_not_run_command(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'linux',
        })

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_runs_fixed_command_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'answer', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))
