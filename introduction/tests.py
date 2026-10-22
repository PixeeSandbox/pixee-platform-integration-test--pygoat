from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def test_cmd_lab_uses_argument_list_without_shell(self):
        User = get_user_model()
        user = User.objects.create_user(username='cmduser', password='testpass123')
        self.client.force_login(user)

        malicious_domain = 'example.com; touch /tmp/pwned'
        mock_process = Mock()
        mock_process.communicate.return_value = (b'', b'')

        with patch('introduction.views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': malicious_domain, 'os': 'linux'}
            )

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', malicious_domain])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], __import__('subprocess').PIPE)
        self.assertEqual(kwargs['stderr'], __import__('subprocess').PIPE)
