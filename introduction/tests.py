from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionTests(TestCase):
    def test_cmd_lab3_rejects_command_injection_domain(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post(
                reverse('Command Injection Lab 3'),
                {'domain': 'example.com; echo injected', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
