from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlabuser', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab_uses_argv_form_for_windows_branch(self):
        malicious_domain = 'example.com; whoami'
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'win-output', b'')

            response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', malicious_domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_cmd_lab_uses_argv_form_for_default_branch(self):
        malicious_domain = 'example.com; whoami'
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'dig-output', b'')

            response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', malicious_domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
