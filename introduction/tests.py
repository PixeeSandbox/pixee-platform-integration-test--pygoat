from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_as_authenticated_user(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return other_views.cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_containing_shell_syntax(self, popen):
        response = self.post_as_authenticated_user({
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.post_as_authenticated_user({
            'domain': 'example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
