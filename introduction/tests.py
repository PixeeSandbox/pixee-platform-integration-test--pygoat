from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import _is_safe_hostname, cmd_lab


class CommandInjectionSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )

    def _build_request(self, domain, os_choice='linux'):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': domain, 'os': os_choice},
        )
        request.user = self.user
        return request

    def test_safe_hostname_helper_accepts_normal_hostname(self):
        self.assertTrue(_is_safe_hostname('example.com'))

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_vector_for_safe_hostname(self, run_mock):
        run_mock.return_value = Mock(stdout='lookup ok', stderr='')

        response = cmd_lab(self._build_request('https://www.example.com', 'win'))

        run_mock.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_shell_metacharacters_before_command_execution(self, run_mock):
        response = cmd_lab(self._build_request('example.com; rm -rf /'))

        run_mock.assert_not_called()
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_whitespace_before_command_execution(self, run_mock):
        response = cmd_lab(self._build_request('example.com bad'))

        run_mock.assert_not_called()
        self.assertEqual(response.status_code, 200)
