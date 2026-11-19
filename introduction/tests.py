from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post(self, domain):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': 'linux'})
        request.user = Mock(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, popen, render):
        process = Mock()
        process.communicate.return_value = (b'lookup result', b'')
        popen.return_value = process

        other_views.cmd_lab3(self._post('https://www.example.com'))

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_invalid_domain_is_rejected_without_starting_process(self, popen, render):
        for domain in ('example.com;whoami', 'example.com && whoami', '-example.com', 'bad_label.example.com'):
            with self.subTest(domain=domain):
                other_views.cmd_lab3(self._post(domain))

        popen.assert_not_called()
