import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_safe_argv_and_shell_false(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('lookup ok', response.content.decode())
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
