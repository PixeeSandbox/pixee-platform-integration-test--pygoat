from unittest.mock import patch
from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_syntax_in_domain(self, mock_popen):
        request = self.request_factory.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_runs_valid_hostname_without_a_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.request_factory.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
