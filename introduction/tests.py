from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false_for_valid_domain(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'output', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
