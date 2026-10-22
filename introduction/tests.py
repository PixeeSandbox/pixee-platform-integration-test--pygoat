from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_argument_list(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'dns output', b'')

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'https://www.example.com', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertContains(response, 'dns output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
