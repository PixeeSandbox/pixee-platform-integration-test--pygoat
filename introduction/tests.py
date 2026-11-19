import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_validates_domain_and_uses_argument_list(self, popen):
        invalid_request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        invalid_request.user = self.user

        response = cmd_lab3(invalid_request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        popen.return_value = process
        valid_request = self.factory.post('/cmd_lab3', {'domain': 'www.example.com', 'os': 'win'})
        valid_request.user = self.user

        response = cmd_lab3(valid_request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
