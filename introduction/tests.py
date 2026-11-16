from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain or OS selector')
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_executes_accepted_domain_without_a_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'www.example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'www.example.com'],
            shell=False,
            stdout=-1,
            stderr=-1,
        )
