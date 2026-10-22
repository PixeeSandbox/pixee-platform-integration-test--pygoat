from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_without_shell_execution(self):
        user = User.objects.create_user(username='cmdlab3user', password='password123')
        self.client.force_login(user)

        malicious_domain = 'example.com; echo injected'
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': malicious_domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'injected')
        mock_popen.assert_not_called()
