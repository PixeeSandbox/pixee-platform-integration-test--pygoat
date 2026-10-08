from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_uses_argv_list_and_disables_shell(self):
        user = get_user_model().objects.create_user(username='testuser', password='password123')
        self.client.force_login(user)
        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
