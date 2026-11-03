import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='test-password',
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'windows output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.Example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_non_windows(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'linux output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab',
            {'domain': '8.8.8.8', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(mock_popen.call_args.args[0], ['dig', '8.8.8.8'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)
