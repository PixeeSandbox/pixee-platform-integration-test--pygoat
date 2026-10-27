from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123',
        )

    def test_cmd_lab_uses_argv_list_for_valid_hostname(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = Mock()
            process.communicate.return_value = (b'example output', b'')
            mock_popen.return_value = process

            response = cmd_lab(request)

        self.assertIsInstance(response, HttpResponse)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, 'example output')

    def test_cmd_lab_rejects_malicious_hostname(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; id', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertIsInstance(response, HttpResponse)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
