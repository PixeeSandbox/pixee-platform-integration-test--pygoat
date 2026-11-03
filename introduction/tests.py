from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='testpassword123'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_list_arguments_for_dig(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'dig output', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;cat /etc/passwd',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com;cat /etc/passwd'],
            stdout=-1,
            stderr=-1,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_list_arguments_for_nslookup(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'nslookup output', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;cat /etc/passwd',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com;cat /etc/passwd'],
            stdout=-1,
            stderr=-1,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
