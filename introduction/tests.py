from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='testpassword123',
        )

    def _build_request(self, domain, os='linux'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os})
        request.user = self.user
        return request

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_without_running_subprocess(self, mock_run):
        request = self._build_request('example.com;id')

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_fixed_argument_list_for_benign_domain(self, mock_run):
        mock_run.return_value = MagicMock(stdout='lookup ok', stderr='')
        request = self._build_request('example.com', os='win')

        response = cmd_lab(request)

        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
