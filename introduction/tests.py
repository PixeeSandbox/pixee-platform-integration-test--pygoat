from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os="linux"):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.render', return_value=HttpResponse())
    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen, render):
        response = views.cmd_lab(self.post_cmd_lab('example.com; touch /tmp/pwned'))

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    def test_valid_hostname_uses_selected_utility_without_shell(self):
        for os, executable in [('linux', 'dig'), ('win', 'nslookup')]:
            with self.subTest(os=os):
                with patch('introduction.views.subprocess.Popen') as popen, \
                        patch('introduction.views.render', return_value=HttpResponse()):
                    popen.return_value.communicate.return_value = (b'lookup output', b'')
                    response = views.cmd_lab(self.post_cmd_lab('example.com', os))

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, 'example.com'],
                    shell=False,
                    stdout=views.subprocess.PIPE,
                    stderr=views.subprocess.PIPE
                )
