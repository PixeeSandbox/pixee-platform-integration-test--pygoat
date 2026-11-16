import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        request = self.request_factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_domain_with_shell_metacharacters_is_rejected(self, mock_popen):
        request = self.request_factory.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
