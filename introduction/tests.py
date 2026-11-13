from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_rejects_injection_shaped_domain(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'win',
            })

        popen.assert_not_called()
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'Invalid domain')
