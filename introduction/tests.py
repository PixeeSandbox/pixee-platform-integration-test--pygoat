from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_uses_separate_arguments_valid_hostname(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        process = SimpleNamespace(communicate=lambda: (b'lookup output', b''))

        with patch('introduction.views.subprocess.Popen', return_value=process) as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once()
        self.assertEqual(popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(popen.call_args.kwargs['shell'])

    def test_rejects_shell_syntax_without_starting_process(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
