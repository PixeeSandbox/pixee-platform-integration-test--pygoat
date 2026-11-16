from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_is_passed_as_argument_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'www.example.com', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_uses_dig_for_non_windows_os(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        views.cmd_lab(request)

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
