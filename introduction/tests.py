from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def test_rejects_hostname_with_shell_syntax(self):
        user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com; id', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
