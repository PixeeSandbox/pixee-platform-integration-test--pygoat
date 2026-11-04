from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch
import subprocess
from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'example', b'')

            cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
