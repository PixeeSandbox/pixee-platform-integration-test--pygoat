from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3ViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_windows_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'win-out', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'win-out')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_non_windows_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'linux-out', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'linux-out')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_invalid_domain_without_execution(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
        mock_popen.assert_not_called()
