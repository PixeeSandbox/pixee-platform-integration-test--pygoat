from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_separate_arguments_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)

    @patch('introduction.views.subprocess.Popen')
    def test_shell_syntax_in_domain_is_rejected(self, popen):
        self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})

        popen.assert_not_called()
