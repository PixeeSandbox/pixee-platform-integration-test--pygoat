from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123'
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = MagicMock(stdout='resolved', stderr='')
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_injection_characters_before_subprocess(self, mock_run):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com;id', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        mock_run.assert_not_called()
