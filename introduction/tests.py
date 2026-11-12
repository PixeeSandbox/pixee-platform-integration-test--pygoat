from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_shell_injection_domain(self):
        user = get_user_model().objects.create_user(username='cmd_test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; whoami',
                'os': 'linux',
            })

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
