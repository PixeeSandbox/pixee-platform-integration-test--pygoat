from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='cmduser', password='password123')

    def test_cmd_lab_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com; whoami', 'os': 'win'},
        )
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()

    def test_cmd_lab_invokes_popen_with_argument_list(self):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': ' https://www.example.com ', 'os': 'win'},
        )
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b'example.com response', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertIn(b'example.com response', response.content)
