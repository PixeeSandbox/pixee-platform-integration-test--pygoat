from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123'
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_run):
        self.client.force_login(self.user)
        mock_run.return_value.stdout = 'Lookup OK\n'
        mock_run.return_value.stderr = ''

        response = self.client.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            capture_output=True,
            text=True,
        )
        self.assertContains(response, 'Lookup OK')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_run):
        self.client.force_login(self.user)

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
