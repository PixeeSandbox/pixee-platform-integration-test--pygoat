import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123',
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; rm -rf /',
                'os': 'linux',
            })

        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'lookup ok', b'')

            response = self.client.post('/cmd_lab', {
                'domain': 'example.com',
                'os': 'linux',
            })

        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
