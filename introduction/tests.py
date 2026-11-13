from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com;echo INJECTED', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain or hostname')
        self.assertNotContains(response, 'INJECTED')
        popen.assert_not_called()
