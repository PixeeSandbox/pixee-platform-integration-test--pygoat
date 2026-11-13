from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CommandLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='command-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_running_command(self, popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'linux'})

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_safe_argument_list(self, popen):
        popen.return_value.communicate.return_value = (b'answer', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertContains(response, 'answer')
        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertIs(kwargs['shell'], False)
