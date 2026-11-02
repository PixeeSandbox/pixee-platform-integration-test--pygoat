from unittest.mock import ANY, Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_injection(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; echo INJECTED',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('INJECTED', response.content.decode())
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; echo INJECTED'],
            stdout=ANY,
            stderr=ANY,
        )
