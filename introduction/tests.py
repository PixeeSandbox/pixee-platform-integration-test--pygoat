from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_invalid_domain_input(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': '-bad.com; echo pwned', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_run):
        mock_run.return_value = Mock(stdout='example output\n', stderr='')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'example output\n')
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, check=False)
