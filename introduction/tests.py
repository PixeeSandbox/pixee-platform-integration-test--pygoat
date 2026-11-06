from django.test import TestCase, Client
from unittest.mock import Mock, patch

from django.contrib.auth.models import User


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'out', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
