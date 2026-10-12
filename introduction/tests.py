from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false(self, mock_popen):
        self.client.force_login(self.user)
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
