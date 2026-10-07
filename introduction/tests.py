from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!',
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_before_command_execution(self, mock_run):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com;id', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argv_list_for_valid_domain(self, mock_run):
        mock_run.return_value.stdout = b''
        mock_run.return_value.stderr = b''
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'Output')
