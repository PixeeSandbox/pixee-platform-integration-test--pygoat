from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, operating_system='linux'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': operating_system})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, mock_popen, mock_render):
        self.post_cmd_lab('example.com; touch /tmp/pwned')

        mock_popen.assert_not_called()

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_argument_list(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        self.post_cmd_lab('example.com')
        self.post_cmd_lab('example.com', 'win')

        self.assertEqual(mock_popen.call_args_list[0].args[0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args_list[0].kwargs['shell'])
        self.assertEqual(mock_popen.call_args_list[1].args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args_list[1].kwargs['shell'])
        self.assertEqual(mock_popen.call_count, 2)
