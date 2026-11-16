from unittest.mock import patch
from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_rejects_invalid_domain(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            views.cmd_lab(request)

        popen.assert_not_called()

    def test_cmd_lab_passes_hostname_as_argument(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'lookup output', b'')
            views.cmd_lab(request)

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
