import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username='tester')

    def post_request(self, domain):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': 'linux'})
        request.user = self.user
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen):
        response = cmd_lab3(self.post_request('example.com; whoami'))

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)

    @patch('introduction.other_views.subprocess.Popen')
    def test_runs_valid_hostname_without_a_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'example.com', b'')

        cmd_lab3(self.post_request('example.com'))

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
