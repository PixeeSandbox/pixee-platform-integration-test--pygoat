from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_allows_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'ok', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertContains(response, 'ok')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
