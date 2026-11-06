from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _build_request(self, domain, os_value):
        request = self.factory.post('/cmd_lab', data={'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.views.subprocess.run', return_value=SimpleNamespace(stdout='lookup ok', stderr=''))
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_run):
        response = cmd_lab(self._build_request('https://www.example.com', 'linux'))

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True, check=False)
        self.assertIn('lookup ok', response.content.decode())

    @patch('introduction.views.subprocess.run', return_value=SimpleNamespace(stdout='lookup ok', stderr=''))
    def test_cmd_lab_selects_nslookup_for_windows_and_dig_otherwise(self, mock_run):
        cmd_lab(self._build_request('example.com', 'win'))
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, check=False)

        mock_run.reset_mock()

        cmd_lab(self._build_request('example.org', 'linux'))
        mock_run.assert_called_once_with(['dig', 'example.org'], capture_output=True, text=True, check=False)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_without_calling_subprocess(self, mock_run):
        response = cmd_lab(self._build_request('example.com;id', 'win'))

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
