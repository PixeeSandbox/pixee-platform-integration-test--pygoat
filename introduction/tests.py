from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='testpass123',
        )

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        self.client.force_login(self.user)

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        self.client.force_login(self.user)
        mock_run.return_value = MagicMock(stdout='resolved\n', stderr='')

        response = self.client.post('/cmd_lab', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)
        self.assertContains(response, 'resolved')
