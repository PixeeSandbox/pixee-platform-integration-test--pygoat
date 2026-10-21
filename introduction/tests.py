from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_uses_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('lookup output', response.content.decode())
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
