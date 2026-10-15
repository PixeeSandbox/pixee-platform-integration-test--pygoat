from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='secure-password-123'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'resolved', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertContains(response, 'resolved')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malformed_hostname_before_subprocess(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
