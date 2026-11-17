from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CommandInjectionTests(TestCase):
    def test_invalid_domain_does_not_execute_command(self):
        user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as process:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'linux',
            })

        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertContains(response, 'Invalid domain')
        process.assert_not_called()
