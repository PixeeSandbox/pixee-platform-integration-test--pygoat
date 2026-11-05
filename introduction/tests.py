from django.contrib.auth import get_user_model
from django.test import TestCase

from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )
        self.url = '/cmd_lab'

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_hostname_uses_list_and_no_shell(self, mock_popen):
        self.assertTrue(self.client.login(username='tester', password='password123'))
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output\n', b'')

        response = self.client.post(
            self.url,
            {'domain': 'https://www.example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example output')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_subprocess(self, mock_popen):
        self.assertTrue(self.client.login(username='tester', password='password123'))

        response = self.client.post(
            self.url,
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
