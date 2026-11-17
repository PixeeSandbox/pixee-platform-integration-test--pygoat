from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, data):
        request = self.factory.post('/cmd_lab/', data)
        request.user = type('AuthenticatedUser', (), {'is_authenticated': True})()
        return views.cmd_lab(request)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_fixed_command_arguments(self, popen, render):
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        popen.return_value = process

        self.post_cmd_lab({'domain': 'example.com', 'os': 'win'})

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_hostname_with_shell_metacharacters_is_rejected(self, popen, render):
        self.post_cmd_lab({'domain': 'example.com; whoami', 'os': 'win'})

        popen.assert_not_called()
        render.assert_called_once()
