from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_command_injection_payload(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {
                'domain': 'example.com; whoami',
                'os': 'win',
            },
        )

        self.assertContains(response, 'Invalid domain')
