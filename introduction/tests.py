from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_rejects_shell_metacharacters_without_invoking_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_valid_hostname_passed_as_argument_list(self, mock_run):
        mock_run.return_value = Mock(stdout='resolver output', stderr='')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertTrue(kwargs.get('capture_output'))
        self.assertTrue(kwargs.get('text'))
        self.assertContains(response, 'resolver output')
