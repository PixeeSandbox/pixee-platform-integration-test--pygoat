from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain supplied')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], -1)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], -1)
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertEqual(response.context['output'], 'output')
