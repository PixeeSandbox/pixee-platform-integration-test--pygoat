from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_command_injection(self):
        user_model = get_user_model()
        user_model.objects.create_user(username='cmdtest', password='test-password')
        self.client.login(username='cmdtest', password='test-password')

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
