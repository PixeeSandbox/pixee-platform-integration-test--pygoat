from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmd_user',
            password='StrongPass123!',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_for_benign_domain(self, mock_run):
        mock_run.return_value.stdout = 'lookup ok\n'
        mock_run.return_value.stderr = ''

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[0][0], ['nslookup', 'example.com'])
        self.assertNotIn(';', str(mock_run.call_args[0][0]))
        self.assertContains(response, 'lookup ok')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Invalid domain')
