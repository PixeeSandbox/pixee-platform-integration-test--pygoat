from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os})
        request.user = Mock(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_starting_process(self, popen):
        response = self.post_cmd_lab('example.com; whoami')

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.subprocess.Popen')
    def test_runs_valid_hostname_with_fixed_executable_and_arguments(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.post_cmd_lab('example.com', os='win')

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        process.communicate.assert_called_once_with()
        self.assertEqual(response.status_code, 200)
