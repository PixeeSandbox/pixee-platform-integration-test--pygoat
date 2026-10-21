from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpassword123',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_subprocess(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'bad.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
