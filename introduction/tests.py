from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch


class CommandInjectionLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='cmd-lab-user', password='password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post(
                reverse('Command Injection Lab 3'),
                {'domain': 'example.com; whoami', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'Invalid domain')
        popen.assert_not_called()
