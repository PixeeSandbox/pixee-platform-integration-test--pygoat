from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_syntax(self, popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_runs_valid_hostname_without_a_shell(self, popen):
        popen.return_value.communicate.return_value = (b'example.com', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once()
        self.assertEqual(popen.call_args.args[0], ['dig', 'example.com'])
        self.assertIs(popen.call_args.kwargs['shell'], False)
