from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmdlabuser', password='password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'output', b'')

        self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)

    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
