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
    def test_cmd_lab_valid_hostname_uses_argument_list(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        self.post_cmd_lab('example.com')

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_windows_choice_uses_nslookup_executable(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        views.cmd_lab(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_missing_hostname_rejected_without_subprocess(self, popen):
        response = self.post_cmd_lab('')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_shell_metacharacters_rejected_without_subprocess(self, popen):
        response = self.post_cmd_lab('example.com; touch /tmp/injected')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        popen.assert_not_called()
