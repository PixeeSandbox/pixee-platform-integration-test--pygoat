from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CmdLab3ValidationTests(TestCase):
    def test_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='tester', password='safe-password123')
        client = Client()
        client.force_login(user)

        with patch('introduction.other_views.subprocess.run') as mocked_run:
            response = client.post('/cmd_lab3', {'domain': 'example.com; cat /etc/passwd', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mocked_run.assert_not_called()
