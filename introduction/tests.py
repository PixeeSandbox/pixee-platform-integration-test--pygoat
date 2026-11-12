from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = Mock(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_syntax_in_domain(self, popen, render):
        request = self.post({'domain': 'example.com; whoami', 'os': 'linux'})
        other_views.cmd_lab3(request)

        popen.assert_not_called()
        render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain name'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_argument_without_shell(self, popen, render):
        popen.return_value.communicate.return_value = (b'lookup result', b'')
        request = self.post({'domain': 'example.com', 'os': 'linux'})

        other_views.cmd_lab3(request)

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookup result'},
        )
