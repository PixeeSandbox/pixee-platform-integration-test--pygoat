from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='testpassword123',
        )

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_injection_input(self, mock_run, mock_popen):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com; whoami', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_run.assert_not_called()
        mock_popen.assert_not_called()
