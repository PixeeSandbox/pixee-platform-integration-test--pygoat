from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
        )

    def test_cmd_lab3_rejects_malicious_domain_without_running_subprocess(self):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.run') as mock_run:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    def test_cmd_lab3_uses_safe_argv_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user
        process = MagicMock(stdout='example.com: 93.184.216.34\n', stderr='')

        with patch('introduction.other_views.subprocess.run', return_value=process) as mock_run:
            response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertFalse(mock_run.call_args.kwargs.get('shell', False))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com: 93.184.216.34')
