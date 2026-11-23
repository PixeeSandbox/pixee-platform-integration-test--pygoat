from django.test import TestCase
from django.test import RequestFactory
from types import SimpleNamespace
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_shell_injection_domain(self):
        request = RequestFactory().post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
