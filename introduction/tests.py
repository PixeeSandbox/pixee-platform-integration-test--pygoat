from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; rm -rf /',
            'os': 'win',
        })

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_with_shell_disabled_for_valid_hostname(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'win',
        })

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
