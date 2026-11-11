from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def test_invalid_domain_rejected_before_command_execution(self):
        user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as process:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; touch /tmp/injected', 'os': 'win'})

        self.assertContains(response, 'Invalid domain')
        process.assert_not_called()
