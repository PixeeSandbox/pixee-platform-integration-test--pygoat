from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cmduser', password='safe-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.subprocess.run')
    def test_malicious_domain_is_rejected_before_subprocess_execution(self, mock_run, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com;id',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.subprocess.run')
    def test_benign_hostname_uses_safe_argument_list_execution(self, mock_run, mock_popen):
        mock_run.return_value.stdout = 'lookup output\n'
        mock_run.return_value.stderr = ''

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        mock_popen.assert_not_called()
        self.assertContains(response, 'lookup output')
