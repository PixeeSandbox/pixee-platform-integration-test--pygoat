import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='secret123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_executes_valid_domain_using_argument_list(self, mock_run):
        mock_run.return_value = Mock(stdout='resolved\n', stderr='')

        response = self.client.post('/cmd_lab', {'domain': 'Example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertContains(response, 'resolved')
