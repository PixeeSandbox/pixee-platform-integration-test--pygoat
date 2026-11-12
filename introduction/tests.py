from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_rejects_domain_with_shell_metacharacters(self):
        request = self.request_factory.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        with patch('introduction.views.render') as render, patch('introduction.views.subprocess.Popen') as popen:
            views.cmd_lab(request)

        popen.assert_not_called()
        render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})

    def test_invokes_fixed_executable_with_valid_domain(self):
        request = self.request_factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.views.render'), patch('introduction.views.subprocess.Popen', return_value=process) as popen:
            views.cmd_lab(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
