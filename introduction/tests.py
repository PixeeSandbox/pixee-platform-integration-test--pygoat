import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.url = reverse('Command Injection Lab')

    def test_cmd_lab_rejects_malicious_domain_before_process_execution(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                self.url,
                {'domain': 'example.com; id', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        self.client.force_login(self.user)
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')

        response = self.client.post(
            self.url,
            {'domain': 'example.com', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertContains(response, 'example output')
