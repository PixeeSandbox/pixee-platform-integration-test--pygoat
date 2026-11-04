from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_hostname_uses_argv_and_no_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'answer', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', '--', 'example.com'])
        self.assertFalse(kwargs.get('shell'))

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_missing_or_blank_domain(self, mock_popen):
        for payload in [{'os': 'linux'}, {'domain': '', 'os': 'linux'}]:
            with self.subTest(payload=payload):
                response = self.client.post('/cmd_lab3', payload)
                self.assertEqual(response.status_code, 200)
                mock_popen.assert_not_called()
                mock_popen.reset_mock()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_option_style_payloads(self, mock_popen):
        for payload in ['-x', '--help']:
            with self.subTest(payload=payload):
                response = self.client.post('/cmd_lab3', {'domain': payload, 'os': 'linux'})
                self.assertEqual(response.status_code, 200)
                mock_popen.assert_not_called()
                mock_popen.reset_mock()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malformed_hostnames_and_metacharacters(self, mock_popen):
        for payload in ['foo..bar', 'bad-.example', 'example.com;id']:
            with self.subTest(payload=payload):
                response = self.client.post('/cmd_lab3', {'domain': payload, 'os': 'linux'})
                self.assertEqual(response.status_code, 200)
                mock_popen.assert_not_called()
                mock_popen.reset_mock()
