import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_runs_lookup_without_a_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup result')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_missing_or_invalid_domain_is_rejected(self, mock_popen):
        for data in ({'os': 'linux'}, {'domain': 'example.com; whoami', 'os': 'linux'}):
            with self.subTest(data=data):
                response = self.client.post('/cmd_lab3', data)
                self.assertEqual(response.status_code, 400)

        mock_popen.assert_not_called()
