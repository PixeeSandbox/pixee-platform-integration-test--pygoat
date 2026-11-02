from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import ANY, patch


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_blocks_shell_injection(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='password123')
        client = Client()
        self.assertTrue(client.login(username='testuser', password='password123'))

        malicious_domain = 'example.com; echo hacked'
        mock_process = type('MockProcess', (), {
            'communicate': lambda self: (b'lookup output', b'')
        })()

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = client.post('/cmd_lab3', {'domain': malicious_domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', malicious_domain],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', malicious_domain])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
