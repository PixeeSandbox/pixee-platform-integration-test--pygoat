from unittest.mock import ANY, Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    def _post_and_assert_command(self, os_value, expected_command):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': os_value})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            expected_command,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    def test_cmd_lab3_uses_list_command_for_dig(self):
        self._post_and_assert_command('linux', ['dig', 'example.com'])

    def test_cmd_lab3_uses_list_command_for_nslookup(self):
        self._post_and_assert_command('win', ['nslookup', 'example.com'])
