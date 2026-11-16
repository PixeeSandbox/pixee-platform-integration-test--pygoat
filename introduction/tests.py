from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd_lab3_test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters_in_domain(self, popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_uses_argument_list_for_valid_hostname(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
