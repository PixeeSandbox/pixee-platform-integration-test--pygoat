from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_input(self):
        user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='StrongPassword123!'
        )
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; id',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain name. Please enter a valid hostname.')
        mock_popen.assert_not_called()
