import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_injection_shaped_domain_does_not_start_process(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')

    def test_valid_domain_uses_fixed_executable_without_shell(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen:
            response = cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
