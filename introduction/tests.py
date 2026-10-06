from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='s3cret-pass')
        self.url = '/cmd_lab3'
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argv_and_renders_output(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = ('resolved output', '')

        response = self.client.post(self.url, {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertIn('resolved output', response.content.decode())

    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected_before_subprocess(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn('Something went wrong', response.content.decode())
