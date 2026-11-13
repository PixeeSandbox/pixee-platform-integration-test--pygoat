from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_rejects_shell_metacharacters_before_execution(self):
        user = get_user_model().objects.create_user(username='cmd_test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; id'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
