from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandLabTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)
        self.url = reverse('Command Injection Lab')

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_safe_argument_list(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'linux'})

        self.assertContains(response, 'lookup output')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertIs(kwargs['shell'], False)
