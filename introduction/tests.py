import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_injection(self):
        user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(user)
        payload = 'example.com; echo injected'

        fake_process = Mock()
        fake_process.communicate.return_value = (b'safe output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=fake_process) as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': payload, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('injected', response.content.decode())
        mock_popen.assert_called_once_with(
            ['dig', payload],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
