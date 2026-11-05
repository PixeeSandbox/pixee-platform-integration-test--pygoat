from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

import introduction.other_views as other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)

    def test_cmd_lab3_uses_safe_argument_list_for_normalized_domain(self):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'https://www.example.com', 'os': 'linux'},
        )
        request.user = self.user

        mock_process = Mock()
        mock_process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
