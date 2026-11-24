from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def test_rejects_domain_with_shell_operators(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
