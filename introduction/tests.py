import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmduser', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_runs_lookup_with_validated_domain_as_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
