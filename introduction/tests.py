import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='test-password',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_safe_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab', {
            'domain': 'https://www.example.com; rm -rf /',
            'os': 'linux',
        })
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
