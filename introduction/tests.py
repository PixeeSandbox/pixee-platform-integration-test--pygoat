from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_domain_with_shell_metacharacters_is_rejected(self, popen):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; touch /tmp/injected', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
