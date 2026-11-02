from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_uses_argument_vector_and_disables_shell(self):
        User = get_user_model()
        User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        mock_process = Mock()
        mock_process.communicate.return_value = (b'output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'example.com; whoami', 'os': 'nix'}
            )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com; whoami'])
        self.assertFalse(kwargs['shell'])
