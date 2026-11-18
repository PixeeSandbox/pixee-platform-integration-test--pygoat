from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLab3CommandInjectionTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_injection_hostname_without_running_command(self, popen):
        response = self.client.post(
            reverse('Command Injection Lab 3'),
            {'domain': 'example.com; whoami', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
