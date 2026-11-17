from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_running_command(self, mock_popen):
        response = self.post_cmd_lab('example.com; whoami')

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_fixed_utility_and_argument_list(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup result', b'')

        self.post_cmd_lab('https://www.example.com', os='win')

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)
