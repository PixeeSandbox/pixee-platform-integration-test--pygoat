from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import patch
import subprocess

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_as_authenticated_user(self, data):
        request = self.factory.post('/cmd_lab/', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        request = self.post_as_authenticated_user({'domain': 'example.com;whoami', 'os': 'linux'})

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain name', response.content)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.post_as_authenticated_user({'domain': 'https://www.example.com', 'os': 'linux'})

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
