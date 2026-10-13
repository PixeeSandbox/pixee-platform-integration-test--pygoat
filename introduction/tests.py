import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-user', password='pass12345')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_executes_benign_domain_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        self.client.force_login(self.user)
        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup ok')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')
