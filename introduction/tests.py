from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='password123',
        )

    def test_cmd_lab_rejects_shell_metacharacters(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'example.com; id', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_cmd_lab_allows_valid_domain(self):
        self.client.force_login(self.user)
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'example.com', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
