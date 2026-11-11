from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_starting_process(self, popen):
        response = self.post_cmd_lab('example.com; touch /tmp/injected')

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_is_passed_as_separate_argument_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.post_cmd_lab('example.com')

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
