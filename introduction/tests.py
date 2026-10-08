from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_without_shell_execution(self):
        user = User.objects.create_user(username='alice', password='password123')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'example.com; cat /etc/passwd', 'os': 'win'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
