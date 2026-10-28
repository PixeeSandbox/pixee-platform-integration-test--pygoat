from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_list_based_subprocess_for_valid_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_hostname_before_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
