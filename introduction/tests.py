from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; touch /tmp/cmd-lab3-test',
                'os': 'win',
            })

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
