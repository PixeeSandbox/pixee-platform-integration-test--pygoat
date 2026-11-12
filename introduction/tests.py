import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_post_runs_fixed_executable_and_renders_output(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup result', b'lookup warning')

        response = self.client.post(self.url, {'domain': 'https://www.example.com', 'os': 'win'})

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertContains(response, 'lookup resultlookup warning')

    @patch('introduction.other_views.subprocess.Popen')
    def test_injection_shaped_hostname_is_rejected(self, popen):
        response = self.client.post(
            self.url,
            {'domain': 'example.com; whoami', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
