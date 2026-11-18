import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTest(TestCase):
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_passes_domain_as_separate_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
        user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.force_login(user)
        domain = 'example.com; touch /tmp/injected'

        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': domain,
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', domain],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
