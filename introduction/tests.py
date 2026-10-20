from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def test_rejects_malicious_domain_input(self):
        user = User.objects.create_user(username='tester', password='safe-password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com; touch /tmp/pwned', 'os': 'win'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mocked_popen.assert_not_called()
