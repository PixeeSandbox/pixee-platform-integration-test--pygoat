from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self._create_user()
        self.client.force_login(self.user)

    def _create_user(self):
        User = get_user_model()
        return User.objects.create_user(username='tester', password='secure-password')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            '/cmd_lab3',
            {
                'domain': 'example.com; whoami',
                'os': 'linux',
            },
        )

        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
