from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        self.client.force_login(self.user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'example.com; rm -rf /', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        self.client.force_login(self.user)
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'example.com', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args[1])
