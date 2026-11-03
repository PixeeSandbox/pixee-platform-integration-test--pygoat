from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; touch /tmp/pwned', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
