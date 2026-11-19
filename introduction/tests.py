from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; touch /tmp/pwned', 'os': 'linux'})
        request.user = self.user

        cmd_lab3(request)

        popen.assert_not_called()
