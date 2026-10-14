from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_valid_domain_uses_argument_list_and_renders_output(self, mock_run):
        process = Mock()
        process.stdout = 'lookup ok\n'
        process.stderr = 'no errors\n'
        mock_run.return_value = process

        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True, check=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn('lookup ok', response.content.decode())
        self.assertIn('no errors', response.content.decode())

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_invalid_domain_without_running_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())
