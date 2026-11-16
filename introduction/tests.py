from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)
        self.assertIn('lookup output', response.content.decode())

    @patch('introduction.views.subprocess.Popen')
    def test_shell_injection_input_does_not_launch_process(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn('Invalid domain', response.content.decode())
