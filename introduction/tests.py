from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import views


class CmdLabTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='tester', password='password123')

    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com; whoami', 'os': 'linux'}
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_win_and_non_win(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'lookup ok', b'')

        test_cases = [
            ('win', ['nslookup', 'example.com']),
            ('linux', ['dig', 'example.com']),
        ]

        for os_value, expected_command in test_cases:
            mock_popen.reset_mock()
            mock_process.communicate.return_value = (b'lookup ok', b'')
            request = self.factory.post(
                '/cmd_lab',
                data={'domain': 'example.com', 'os': os_value}
            )
            request.user = self.user

            response = views.cmd_lab(request)

            self.assertEqual(response.status_code, 200)
            mock_popen.assert_called_once_with(
                expected_command,
                stdout=views.subprocess.PIPE,
                stderr=views.subprocess.PIPE,
            )
