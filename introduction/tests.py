import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmd-user',
            password='StrongPass123!',
        )
        self.client.force_login(self.user)
        self.url = '/cmd_lab'

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, popen):
        response = self.client.post(
            self.url,
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_disables_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        response = self.client.post(
            self.url,
            {'domain': 'example.com', 'os': 'linux'},
        )

        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
