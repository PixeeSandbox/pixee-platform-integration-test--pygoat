from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from unittest.mock import ANY, Mock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example.com\n', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=ANY, stderr=ANY)
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
