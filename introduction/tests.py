from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_passed_as_separate_arguments(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_malicious_hostname_is_rejected(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
