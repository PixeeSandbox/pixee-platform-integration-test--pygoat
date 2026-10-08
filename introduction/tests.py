from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_rejects_malicious_domain_before_process_execution(self, mock_run):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.other_views.subprocess.run')
    def test_uses_dig_with_argument_list_and_shell_disabled(self, mock_run):
        mock_run.return_value = Mock(stdout='dig output', stderr='')

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'linux'},
        )

        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            capture_output=True,
            text=True,
            shell=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dig output')

    @patch('introduction.other_views.subprocess.run')
    def test_uses_nslookup_for_windows_branch_with_argument_list(self, mock_run):
        mock_run.return_value = Mock(stdout='nslookup output', stderr='')

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'win'},
        )

        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            shell=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'nslookup output')
