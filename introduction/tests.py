from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def test_rejects_malicious_domain(self):
        User = get_user_model()
        user = User.objects.create_user(username='alice', password='Password123!')
        self.client.force_login(user)

        malicious_domain = 'example.com; echo injected'
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, malicious_domain)
        mock_popen.assert_not_called()
