from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)
        self.assertIn('stdout', kwargs)
        self.assertIn('stderr', kwargs)
        process.communicate.assert_called_once_with()

    @patch('introduction.views.subprocess.Popen')
    def test_shell_metacharacters_in_hostname_are_rejected(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com; whoami', 'os': 'win'},
        )

        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')

# Create your tests here.
