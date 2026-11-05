from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def test_rejects_shell_metacharacters_in_domain(self):
        User = get_user_model()
        user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'google.com; id', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
