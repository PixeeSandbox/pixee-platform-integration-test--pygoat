from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionLabTests(TestCase):
    def test_rejects_domain_with_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'Non-authoritative answer')
        popen.assert_not_called()
