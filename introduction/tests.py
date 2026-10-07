import subprocess

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.run') as mock_run:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()

    def test_cmd_lab_uses_subprocess_run_with_argument_list(self):
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=['dig', 'example.com'],
                returncode=0,
                stdout='resolved output',
                stderr='',
            )
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved output')
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
