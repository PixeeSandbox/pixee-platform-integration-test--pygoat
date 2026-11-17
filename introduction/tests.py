from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, operating_system):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': operating_system})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    def test_valid_hostname_uses_fixed_executable_without_a_shell(self):
        for operating_system, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(operating_system=operating_system):
                with patch('introduction.views.subprocess.Popen') as popen:
                    popen.return_value.communicate.return_value = (b'lookup result', b'')

                    self.post_cmd_lab('example.com', operating_system)

                    popen.assert_called_once()
                    args, kwargs = popen.call_args
                    self.assertEqual(args[0], [executable, 'example.com'])
                    self.assertIs(kwargs['shell'], False)

    def test_malformed_hostname_is_rejected_without_running_a_process(self):
        for domain in ('example.com; whoami', '-example.com', 'example..com', ''):
            with self.subTest(domain=domain):
                with patch('introduction.views.subprocess.Popen') as popen:
                    self.post_cmd_lab(domain, 'linux')
                    popen.assert_not_called()

    def test_overlong_hostname_is_rejected_without_running_a_process(self):
        domain = 'a' * 254
        with patch('introduction.views.subprocess.Popen') as popen:
            self.post_cmd_lab(domain, 'linux')
            popen.assert_not_called()

    def test_unsupported_operating_system_is_rejected_without_running_a_process(self):
        with patch('introduction.views.subprocess.Popen') as popen:
            self.post_cmd_lab('example.com', 'unknown')
            popen.assert_not_called()
