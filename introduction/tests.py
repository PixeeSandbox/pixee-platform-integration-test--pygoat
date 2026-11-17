import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_without_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_passes_valid_domain_as_argument_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'address output', b'')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
