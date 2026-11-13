import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def post_cmd_lab(self, data):
        request = self.request_factory.post('/cmd_lab', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_malformed_domain_is_rejected_without_running_process(self, popen):
        response = self.post_cmd_lab({'domain': 'example.com; whoami', 'os': 'win'})

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_is_passed_as_safe_argument_vector(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.post_cmd_lab({'domain': 'https://www.example.com', 'os': 'win'})

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
