import subprocess
from types import SimpleNamespace
from unittest.mock import call, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_as_authenticated_user(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        request = self.post_as_authenticated_user({
            'domain': 'example.com; whoami',
            'os': 'win',
        })

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_executable_and_argument_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'dns output', b'')

        for os_value, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_value):
                request = self.post_as_authenticated_user({
                    'domain': 'https://www.example.com',
                    'os': os_value,
                })

                response = cmd_lab3(request)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    popen.call_args,
                    call(
                        [executable, 'example.com'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    ),
                )
                self.assertNotIn('shell', popen.call_args.kwargs)
