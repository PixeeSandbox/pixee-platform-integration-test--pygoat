import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)
        self.url = '/cmd_lab3'

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(self.url, {
            'domain': 'example.com; id',
            'os': 'win',
        })

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        response = self.client.post(self.url, {
            'domain': 'example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        command, = mock_popen.call_args.args
        kwargs = mock_popen.call_args.kwargs
        self.assertEqual(command, ['nslookup', 'example.com'])
        self.assertIs(kwargs.get('stdout'), subprocess.PIPE)
        self.assertIs(kwargs.get('stderr'), subprocess.PIPE)
        self.assertNotIn('shell', kwargs)
