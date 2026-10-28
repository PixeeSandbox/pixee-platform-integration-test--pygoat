from types import SimpleNamespace
from unittest.mock import ANY, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_safe_domain(self, mock_popen):
        process = SimpleNamespace(
            communicate=lambda: (b'lookup output', b'')
        )
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, 'lookup output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
