from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )
        self.url = reverse('Command Injection Lab')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_vector_for_benign_domain(self, mock_popen):
        self.client.force_login(self.user)
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'ok', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {'domain': 'example.com; whoami', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
