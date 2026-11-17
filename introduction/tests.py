from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmdtest', password='test-password')
        self.client = Client()
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/cmd-injection',
            'os': 'linux',
        })

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
