from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args[1]['shell'])

    @patch('introduction.other_views.subprocess.Popen')
    def test_shell_syntax_hostname_is_rejected(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
