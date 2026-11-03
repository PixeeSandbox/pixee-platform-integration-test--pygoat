from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertEqual(mock_popen.call_args.kwargs.get('shell'), False)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
