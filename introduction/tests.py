import subprocess

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'valid output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'valid output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injected_domain_before_popen(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid input')
