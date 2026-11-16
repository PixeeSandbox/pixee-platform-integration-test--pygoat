from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_shell_injection_domain(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com;touch /tmp/injected',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
