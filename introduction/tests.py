from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_syntax(self, mock_popen):
        response = self.post_cmd_lab('example.com; whoami')

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_invokes_utility_with_separate_domain_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'answer', b'')

        response = self.post_cmd_lab('example.com', os='win')

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
