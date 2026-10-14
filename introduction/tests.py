import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_does_not_execute_shell_metacharacters(self):
        User = get_user_model()
        user = User.objects.create_user(username='cmduser', password='pass12345')
        self.assertTrue(self.client.login(username=user.username, password='pass12345'))

        malicious_domain = 'example.com; echo INJECTED'

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'safe output', b'')

            response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'lin'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'safe output')
        self.assertNotContains(response, 'INJECTED')
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['dig', malicious_domain])
        self.assertFalse(called_kwargs['shell'])
        self.assertEqual(called_kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(called_kwargs['stderr'], subprocess.PIPE)
