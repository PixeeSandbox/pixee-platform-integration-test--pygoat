import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_cmd_lab3_valid_domain_uses_argument_list_without_shell(self):
        request = self.request_factory.post('/cmd/', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        with patch('introduction.other_views.subprocess.Popen') as process:
            process.return_value.communicate.return_value = (b'answer', b'')

            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        process.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_cmd_lab3_rejects_invalid_domain_without_running_process(self):
        request = self.request_factory.post('/cmd/', {'domain': '-example.com;id', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as process:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        process.assert_not_called()
