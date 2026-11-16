import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'Invalid domain name')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_nslookup_for_windows_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'lookup error')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'], shell=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'lookup outputlookup error')

    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_dig_for_linux_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'dig output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'dig output')
