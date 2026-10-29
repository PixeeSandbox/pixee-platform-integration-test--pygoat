from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd-user',
            password='test-password',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_domain_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')

        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertIn('valid output', response.content.decode())

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com;id', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertIn('Invalid domain', response.content.decode())
