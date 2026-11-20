import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_as_authenticated_user(self, data):
        request = self.factory.post('/cmd_lab3/', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen):
        response = self.post_as_authenticated_user({
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_invokes_lookup_with_domain_as_separate_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post_as_authenticated_user({'domain': 'example.com', 'os': 'win'})

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
