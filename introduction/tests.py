from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch

# Create your tests here.


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmd_lab_user',
            password='test-password-123'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_valid_hostname_uses_argument_list(self, mock_run):
        mock_run.return_value = Mock(stdout='valid output\n', stderr='')

        response = self.client.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertContains(response, 'valid output')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_hostname(self, mock_run):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid hostname')
        mock_run.assert_not_called()
