from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_without_starting_process(self):
        user = User.objects.create_user(username='cmd_lab_test', password='password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
