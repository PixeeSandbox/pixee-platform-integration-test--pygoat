from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def test_rejects_domain_with_shell_syntax(self):
        user = get_user_model().objects.create_user(username='cmdtest', password='password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as process_launcher:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 400)
        process_launcher.assert_not_called()
