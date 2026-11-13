from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_hostile_domain_without_running_process(self, popen):
        request = self.factory.post('/cmd/', {'domain': 'example.com;whoami', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
