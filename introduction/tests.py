from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_rejects_shell_metacharacters_without_starting_process(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    def test_passes_valid_domain_as_argument_without_shell(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        with patch('introduction.views.subprocess.Popen') as process:
            process.return_value.communicate.return_value = (b'lookup output', b'')

            views.cmd_lab(request)

        args, kwargs = process.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
