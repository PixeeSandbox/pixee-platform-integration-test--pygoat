from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def test_rejects_domain_with_shell_syntax(self):
        request = RequestFactory().post(
            '/cmd_lab3/',
            {'domain': 'example.com; whoami', 'os': 'linux'},
        )
        request.user = type('AuthenticatedUser', (), {'is_authenticated': True})()

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
