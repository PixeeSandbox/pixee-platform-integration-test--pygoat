from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabCommandInjectionTest(TestCase):
    def test_rejects_shell_syntax_without_running_subprocess(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()
