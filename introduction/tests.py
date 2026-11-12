import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_as_authenticated_user(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_injection_payload(self, popen):
        request = self.post_as_authenticated_user({
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_invokes_fixed_executable_with_hostname_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.post_as_authenticated_user({
            'domain': 'example.com',
            'os': 'linux',
        })

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
