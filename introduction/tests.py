from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def test_rejects_injection_shaped_domain(self):
        user = User.objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; whoami',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid domain', status_code=400)
        popen.assert_not_called()
