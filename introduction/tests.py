from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_shell(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example.com', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
