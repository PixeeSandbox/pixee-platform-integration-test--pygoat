from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3SecurityTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters_before_running_process(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
