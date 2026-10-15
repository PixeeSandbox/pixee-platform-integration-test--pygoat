from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3RegressionTest(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        User = get_user_model()
        user = User.objects.create_user(username='cmdlab3user', password='StrongPass123!')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'linux'})

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
