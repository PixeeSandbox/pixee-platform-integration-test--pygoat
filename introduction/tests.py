import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.client.post(self.url, {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_passes_valid_hostname_as_separate_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
