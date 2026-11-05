from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_linux_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_invalid_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
