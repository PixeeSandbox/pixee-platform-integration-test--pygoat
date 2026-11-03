from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import ANY, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )
        self.client = Client()
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_safe_domain_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'stdout', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'lin',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'lin',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
