from unittest.mock import patch, Mock
from types import SimpleNamespace

from django.test import TestCase, RequestFactory

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'lookup result', b'')
        mock_popen.return_value = process
        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_malicious_domain_is_rejected_without_launching_process(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args[0][2], {'output': 'Invalid domain'})
