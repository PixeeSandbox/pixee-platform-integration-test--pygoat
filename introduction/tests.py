from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def test_rejects_domain_with_shell_metacharacters(self):
        request = RequestFactory().post('/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertContains(response, 'Invalid domain')
