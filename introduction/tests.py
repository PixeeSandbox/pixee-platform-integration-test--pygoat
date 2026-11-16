from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, popen):
        response = self.post_cmd_lab({'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_runs_as_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.post_cmd_lab({'domain': 'www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
