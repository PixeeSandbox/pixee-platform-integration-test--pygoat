from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def test_rejects_shell_metacharacters_without_launching_subprocess(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; touch /tmp/pwned',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
