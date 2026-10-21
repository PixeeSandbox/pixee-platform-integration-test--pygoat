import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    def test_rejects_malicious_domain_without_invoking_subprocess(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                self.url,
                {'domain': 'example.com; rm -rf /', 'os': 'linux'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain provided')
        mock_popen.assert_not_called()

    def test_valid_domain_invokes_popen_with_argument_list(self):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = self.client.post(
                self.url,
                {'domain': 'example.com', 'os': 'linux'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertEqual(kwargs.get('shell', False), False)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
