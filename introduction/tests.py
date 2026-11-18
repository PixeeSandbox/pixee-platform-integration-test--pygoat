import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_domain_is_passed_as_a_single_argument_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab', {'domain': 'sub-domain.example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'sub-domain.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_malformed_domain_is_rejected_without_running_command(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/injected', 'os': 'win'})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
