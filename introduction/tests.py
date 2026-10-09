from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import ANY, MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.run')
    def test_valid_domain_uses_argument_list_and_renders_output(self, mock_run):
        mock_process = MagicMock()
        mock_process.stdout = 'dig output\n'
        mock_process.stderr = 'no errors\n'
        mock_run.return_value = mock_process
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dig output')
        self.assertContains(response, 'no errors')
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
            text=True,
        )
        called_args, called_kwargs = mock_run.call_args
        self.assertEqual(called_args[0], ['dig', 'example.com'])
        self.assertFalse(called_kwargs['shell'])
        self.assertEqual(called_kwargs['stdout'], -1)
        self.assertEqual(called_kwargs['stderr'], -1)
        self.assertTrue(called_kwargs['text'])

    @patch('introduction.other_views.subprocess.run')
    def test_malicious_domain_is_rejected_and_subprocess_not_called(self, mock_run):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'domain': 'example.com; ls', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
