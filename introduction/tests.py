import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')
        self.url = reverse('Command Injection Lab')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_invalid_domain(self, mock_run):
        response = self.client.post(
            self.url,
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argv_without_shell(self, mock_run):
        mock_run.return_value = Mock(stdout='lookup ok\n', stderr='')

        response = self.client.post(
            self.url,
            {'domain': 'example.com', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertEqual(kwargs.get('stdout'), subprocess.PIPE)
        self.assertEqual(kwargs.get('stderr'), subprocess.PIPE)
        self.assertTrue(kwargs.get('text'))
        self.assertContains(response, 'lookup ok')
