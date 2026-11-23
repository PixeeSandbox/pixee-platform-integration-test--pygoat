from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def test_shell_metacharacters_in_domain_are_rejected(self):
        request = RequestFactory().post(
            '/cmd_lab3',
            {'domain': 'example.com; touch /tmp/pwned', 'os': 'linux'},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
