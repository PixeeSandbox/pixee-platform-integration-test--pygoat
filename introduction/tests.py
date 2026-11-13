import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_syntax_in_domain(self, popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.test; printf INJECTED',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain name')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_shell_free_argument_list(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'example.test',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.test'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_linux_selection_uses_dig(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'example.test',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.test'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
