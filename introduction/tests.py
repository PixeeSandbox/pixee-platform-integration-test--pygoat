from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def test_rejects_shell_syntax_without_running_subprocess(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
