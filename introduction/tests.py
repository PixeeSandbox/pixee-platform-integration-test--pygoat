from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_executing_shell(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'lookup ok')
