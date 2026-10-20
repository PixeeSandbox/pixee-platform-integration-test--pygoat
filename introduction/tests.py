import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='secret123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_without_popen(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain supplied')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup-ok', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup-ok')
