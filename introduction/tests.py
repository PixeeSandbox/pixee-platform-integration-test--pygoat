from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTest(TestCase):
    def test_rejects_domain_with_shell_metacharacters(self):
        request = RequestFactory().post(
            '/cmd_lab3',
            {'domain': 'example.com; touch /tmp/injected', 'os': 'linux'},
        )
        request.user = User()

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
