from types import SimpleNamespace
from unittest.mock import ANY, Mock, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, popen_mock):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'https://www.example.com; whoami', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        popen_mock.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_valid_hostname(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        popen_mock.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertIn('lookup ok', response.content.decode())
