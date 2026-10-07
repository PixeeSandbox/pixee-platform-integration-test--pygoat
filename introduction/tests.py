from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpassword123'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_safe_non_shell_execution(self, mock_run):
        mock_run.return_value.stdout = 'resolver output\n'
        mock_run.return_value.stderr = ''

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'lin',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            capture_output=True,
            text=True,
        )
        self.assertContains(response, 'resolver output')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; rm -rf /',
            'os': 'lin',
        })

        self.assertEqual(response.status_code, 400)
        mock_run.assert_not_called()
