from unittest.mock import patch
from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        views.cmd_lab(request)

        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
