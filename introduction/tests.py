from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_lookup(self, domain):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)
        return other_views.cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.post_lookup('example.com; touch /tmp/pwned')

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        self.post_lookup('example.com')

        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertIn('stdout', kwargs)
        self.assertIn('stderr', kwargs)
