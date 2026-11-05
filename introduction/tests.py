from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_safe_subprocess_arguments(self, mock_run):
        mock_run.return_value = Mock(stdout='lookup ok\n', stderr='')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_injected_domain(self, mock_run):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_run.assert_not_called()
