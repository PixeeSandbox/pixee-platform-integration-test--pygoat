from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_request(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_running_process(self, mock_popen, mock_render):
        request = self.post_request('example.com;whoami')

        views.cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request, 'Lab/CMD/cmd_lab.html', {"output": "Something went wrong"})

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_runs_valid_domain_as_separate_argument_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'address', b'')
        request = self.post_request('example.com', os='win')

        views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE)
        process.communicate.assert_called_once_with()
        mock_render.assert_called_once_with(
            request, 'Lab/CMD/cmd_lab.html', {"output": "address"})
