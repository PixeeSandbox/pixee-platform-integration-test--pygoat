from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com;whoami', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
