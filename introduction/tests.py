from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_linux_lookup_uses_separate_arguments_and_renders_output(self, run):
        run.return_value.stdout = 'linux stdout'
        run.return_value.stderr = 'linux stderr'

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        run.assert_called_once_with(
            ['dig', 'example.com'], shell=False, stdout=-1, stderr=-1, encoding='utf-8')
        self.assertContains(response, 'linux stdout')
        self.assertContains(response, 'linux stderr')

    @patch('introduction.views.subprocess.run')
    def test_windows_lookup_uses_separate_arguments_and_renders_output(self, run):
        run.return_value.stdout = 'windows stdout'
        run.return_value.stderr = 'windows stderr'

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        run.assert_called_once_with(
            ['nslookup', 'example.com'], shell=False, stdout=-1, stderr=-1, encoding='utf-8')
        self.assertContains(response, 'windows stdout')
        self.assertContains(response, 'windows stderr')

    @patch('introduction.views.subprocess.run')
    def test_invalid_domain_or_os_is_rejected_without_running_command(self, run):
        invalid_requests = (
            {'domain': 'example.com; whoami', 'os': 'linux'},
            {'domain': 'bad..example.com', 'os': 'linux'},
            {'domain': '-bad.example.com', 'os': 'linux'},
            {'domain': 'example.com/path', 'os': 'linux'},
            {'domain': 'a' * 254, 'os': 'linux'},
            {'os': 'linux'},
            {'domain': 'example.com', 'os': 'mac'},
        )

        for post_data in invalid_requests:
            with self.subTest(post_data=post_data):
                response = self.client.post('/cmd_lab', post_data)
                self.assertContains(response, 'Invalid domain or OS selection')

        run.assert_not_called()
