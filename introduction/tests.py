from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='testpass123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab3', data={'domain': 'example.com; id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain name')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_allows_valid_domain_with_safe_process_invocation(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok\n', b'')
        request = self.factory.post('/cmd_lab3', data={'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=-1,
            stderr=-1,
        )
        self.assertContains(response, 'lookup ok')
