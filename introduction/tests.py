import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='TestPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_posts_safe_domain_without_shell(self, mock_run):
        mock_run.return_value.stdout = b'safe-output\n'
        mock_run.return_value.stderr = b''

        response = self.client.post('/cmd_lab', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'safe-output')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com;id',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
