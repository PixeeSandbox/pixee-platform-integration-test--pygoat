from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_rejects_malicious_domain_without_running_subprocess(self, mock_run):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_uses_argument_list_for_valid_hostname(self, mock_run):
        mock_process = type('Process', (), {'returncode': 0, 'stdout': 'ok', 'stderr': ''})()
        mock_run.return_value = mock_process

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        called_args, called_kwargs = mock_run.call_args
        self.assertEqual(called_args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', called_kwargs)
        self.assertFalse(called_kwargs.get('shell', False))
        self.assertEqual(called_kwargs.get('capture_output'), True)
        self.assertEqual(called_kwargs.get('text'), True)
        self.assertContains(response, 'ok')
