from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import ANY, patch


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_execution_for_valid_domains(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})
        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

        mock_popen.reset_mock()
        mock_process.communicate.return_value = (b'example output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'nix'})
        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_execution(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
