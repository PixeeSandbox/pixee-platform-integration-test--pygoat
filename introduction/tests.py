import subprocess
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='testpass123',
        )

    def test_cmd_lab_executes_safe_domain_with_argv(self):
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
