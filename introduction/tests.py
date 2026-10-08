import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='tester', password='pass12345')

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_post_uses_argv_list_and_shell_false(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.Example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertContains(response, 'lookup ok')

    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_rejected_before_popen(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
