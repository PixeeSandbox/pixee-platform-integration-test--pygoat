import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='cmd-test', password='test-password')

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_malformed_domain_without_running_command(self, mock_popen):
        request = self.factory.post('/cmd-lab/', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_runs_lookup_with_executable_and_domain_as_arguments(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd-lab/', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = self.user

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
