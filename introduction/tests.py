import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_valid_domain_uses_fixed_executable_and_argument(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_shell_injection_domain_is_rejected(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
