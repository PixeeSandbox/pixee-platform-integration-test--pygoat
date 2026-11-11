import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_value})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters_without_starting_process(self, popen):
        response = self.post_cmd_lab('example.com;whoami')

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_selected_executable_without_shell_interpretation(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post_cmd_lab('example.com', 'win')

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

