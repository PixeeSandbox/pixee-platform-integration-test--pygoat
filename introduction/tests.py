from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3TestCase(TestCase):
    @patch('introduction.other_views.subprocess.Popen')
    def test_domain_is_passed_as_a_single_argument(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        user = get_user_model().objects.create_user(username='test-user', password='password')
        self.client.force_login(user)
        domain = 'example.com; touch /tmp/injected'

        response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', domain])
        self.assertFalse(kwargs['shell'])
        self.assertIsNotNone(kwargs['stdout'])
        self.assertIsNotNone(kwargs['stderr'])
