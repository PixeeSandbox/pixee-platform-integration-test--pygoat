from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_invokes_nslookup_for_valid_domain(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = get_user_model()(username='test')

        with patch('introduction.other_views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab3(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup output')

    def test_rejects_shell_metacharacters_in_domain(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = get_user_model()(username='test')

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')
