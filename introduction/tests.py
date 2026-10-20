from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='pass12345'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_run):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_allows_valid_hostname(self, mock_run):
        mock_run.return_value = MagicMock(stdout='lookup ok\n', stderr='')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True)
