from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='Password123!'
        )

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_run):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com; whoami', 'os': 'linux'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_secure_subprocess_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout='lookup ok\n', stderr='')
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
        )
        self.assertContains(response, 'lookup ok')
