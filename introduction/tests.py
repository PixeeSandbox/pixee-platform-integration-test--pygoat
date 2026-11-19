import subprocess
from unittest.mock import call, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_valid_hostname_uses_fixed_executable(self, mock_run):
        mock_run.return_value.stdout = 'lookup output'
        mock_run.return_value.stderr = 'lookup error'

        for os_choice, executable in [('win', 'nslookup'), ('linux', 'dig')]:
            with self.subTest(os_choice=os_choice):
                response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': os_choice})

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'lookup output')
                self.assertContains(response, 'lookup error')
                self.assertEqual(mock_run.call_args_list[-1], call(
                    [executable, 'example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True))

    @patch('introduction.views.subprocess.run')
    def test_invalid_hostname_is_rejected_without_running_command(self, mock_run):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid hostname', status_code=400)
        mock_run.assert_not_called()
