import subprocess
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class AuthenticatedUserStub:
    is_authenticated = True


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_rejects_shell_metacharacters_without_starting_process(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'linux',
        })
        request.user = AuthenticatedUserStub()

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    def test_valid_hostname_uses_separate_shell_free_arguments(self):
        for operating_system, executable in (('linux', 'dig'), ('win', 'nslookup')):
            with self.subTest(operating_system=operating_system):
                request = self.factory.post('/cmd_lab', {
                    'domain': 'www.example.com',
                    'os': operating_system,
                })
                request.user = AuthenticatedUserStub()
                with patch('introduction.views.subprocess.Popen') as popen:
                    popen.return_value.communicate.return_value = (b'lookup output', b'')
                    response = cmd_lab(request)

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, 'www.example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
