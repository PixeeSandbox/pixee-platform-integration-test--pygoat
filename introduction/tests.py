import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username='test')

    def post_cmd_lab3(self, domain, os='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os})
        request.user = self.user
        return cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen):
        self.post_cmd_lab3('example.com; touch /tmp/injected')

        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argument_list_for_valid_domain(self, popen):
        popen.return_value.communicate.return_value = (b'', b'')

        self.post_cmd_lab3('example.com')

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
