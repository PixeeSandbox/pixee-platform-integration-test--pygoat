from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')

        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['nslookup', 'example.com'])
        self.assertFalse(called_kwargs.get('shell', False))
        self.assertIn('valid output', response.content.decode())

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen):
        response = self.client.post(reverse('Command Injection Lab 3'), {
            'domain': 'example.com && id',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn('Something went wrong', response.content.decode())
