from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; whoami',
            'os': 'linux',
        })

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
