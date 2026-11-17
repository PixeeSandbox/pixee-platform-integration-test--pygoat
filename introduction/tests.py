import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmdtest', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_injection_like_domain(self, popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'win',
        })

        self.assertEqual(response.context['output'], 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_passes_valid_domain_as_separate_arguments(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
