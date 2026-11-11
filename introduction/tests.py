from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    def test_valid_hostname_invokes_dns_utility_without_shell(self):
        for operating_system, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(operating_system=operating_system):
                request = self.factory.post('/cmd_lab3', {
                    'domain': 'www.example.com',
                    'os': operating_system,
                })
                request.user = SimpleNamespace(is_authenticated=True)

                with patch('introduction.other_views.subprocess.Popen') as popen:
                    popen.return_value.communicate.return_value = (b'lookup output', b'')
                    response = other_views.cmd_lab3(request)

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, 'www.example.com'],
                    shell=False,
                    stdout=other_views.subprocess.PIPE,
                    stderr=other_views.subprocess.PIPE,
                )
