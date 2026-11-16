from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen):
        request = self.factory.post('/cmd-lab/', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_is_passed_as_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd-lab/', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)
