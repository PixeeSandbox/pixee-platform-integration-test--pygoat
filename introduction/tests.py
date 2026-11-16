from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os='win'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_running_process(self, popen):
        response = self.post_cmd_lab('example.com; touch /tmp/pwned')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_runs_fixed_utility_with_hostname_as_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.post_cmd_lab('https://www.example.com')

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE)
