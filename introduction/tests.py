from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabTests(TestCase):
    def test_domain_with_shell_metacharacters_does_not_execute_command(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})

        popen.assert_not_called()
