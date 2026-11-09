from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='cmdlab3user', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com; echo INJECTED_OUTPUT', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'INJECTED_OUTPUT')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = MagicMock(stdout='valid output', stderr=' stderr')

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'win'}
        )

        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid output stderr')
