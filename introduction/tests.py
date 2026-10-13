from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='cmdlabuser',
            password='strong-password-123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_malicious_domain_before_subprocess(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; id', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_uses_argument_list_for_benign_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
