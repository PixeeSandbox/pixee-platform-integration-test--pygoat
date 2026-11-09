from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
