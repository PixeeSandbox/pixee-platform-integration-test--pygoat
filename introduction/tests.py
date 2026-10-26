from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.login(username='cmduser', password='StrongPass123!')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_safe_subprocess_arguments(self, mock_run):
        mock_run.return_value.stdout = 'safe output'
        mock_run.return_value.stderr = ''

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['text'], True)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malformed_domain_without_subprocess(self, mock_run):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )

        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
