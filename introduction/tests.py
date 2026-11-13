import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')

    def test_rejects_shell_metacharacters_without_running_process(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    def test_passes_hostname_as_separate_argument_without_shell(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user
        with patch('introduction.views.subprocess.Popen') as process:
            process.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        process.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
