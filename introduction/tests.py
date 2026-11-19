from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_is_passed_as_argument_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_invalid_domain_is_rejected_without_process_invocation(self, popen):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
