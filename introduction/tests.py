from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_for_safe_hostname(self, mock_run):
        mock_process = MagicMock()
        mock_process.stdout = 'lookup ok\n'
        mock_process.stderr = ''
        mock_run.return_value = mock_process

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_run.assert_called_once_with(['nslookup', 'example.com'], shell=False, capture_output=True, text=True)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
