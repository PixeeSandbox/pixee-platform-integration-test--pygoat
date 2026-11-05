from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlabuser', password='testpassword')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'valid stdout', b'valid stderr')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        self.assertIn(b'valid stdoutvalid stderr', response.content)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)
