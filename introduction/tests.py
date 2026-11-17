import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory
from django.test import TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_passed_as_argument(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self.request_factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_shell_metacharacters_rejected_without_launching_subprocess(self, mock_popen):
        request = self.request_factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid hostname')
