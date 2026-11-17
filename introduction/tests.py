from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_injection_domain(self, popen):
        response = self.post_cmd_lab('example.com; touch /tmp/pwned')

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_invokes_dns_utility_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.post_cmd_lab('example.com')

        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertIs(kwargs['shell'], False)
        self.assertEqual(response.status_code, 200)
