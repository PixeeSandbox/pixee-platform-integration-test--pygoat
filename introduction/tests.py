from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_domain_uses_separate_arguments(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertIn('example output', response.content.decode())

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injected_domain(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_popen.assert_not_called()
