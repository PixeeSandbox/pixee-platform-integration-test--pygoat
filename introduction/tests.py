import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup output', response.content)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
