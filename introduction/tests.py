import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post(self, domain, os='linux'):
        request = self.factory.post('/cmd-lab/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_is_passed_as_argument_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        cmd_lab(self._post('example.com', 'win'))

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_dig_by_default(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        cmd_lab(self._post('example.com'))

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_hostname_with_shell_syntax_is_rejected(self, mock_popen):
        response = cmd_lab(self._post('example.com; touch /tmp/injected'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
