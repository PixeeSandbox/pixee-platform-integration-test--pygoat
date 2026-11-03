from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_post_uses_argument_list_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')
        self.client.force_login(self.user)

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'linux'},
            HTTP_HOST='pygoat.herokuapp.com',
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=mock_popen.call_args.kwargs['stdout'],
            stderr=mock_popen.call_args.kwargs['stderr'],
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injection_style_domain_without_subprocess(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com; id', 'os': 'linux'},
            HTTP_HOST='pygoat.herokuapp.com',
        )

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
