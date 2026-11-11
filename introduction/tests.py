from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CommandInjectionDomainTests(TestCase):
    def test_cmd_lab3_rejects_command_injection_domain(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; whoami',
                'os': 'linux',
            })

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
