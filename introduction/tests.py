from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def test_domain_with_shell_metacharacters_is_rejected(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com; touch /tmp/injected', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
