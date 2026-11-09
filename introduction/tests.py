from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_rejects_injection_shaped_domain_without_launching_process(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch.object(other_views.subprocess, 'Popen') as popen, patch.object(other_views, 'render') as render:
            other_views.cmd_lab3(request)

        popen.assert_not_called()
        self.assertEqual(render.call_args[0][2], {'output': 'Invalid domain'})

    def test_launches_fixed_dns_command_for_valid_domain(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        process = SimpleNamespace(communicate=lambda: (b'lookup output', b''))

        with patch.object(other_views.subprocess, 'Popen', return_value=process) as popen, patch.object(other_views, 'render'):
            other_views.cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
