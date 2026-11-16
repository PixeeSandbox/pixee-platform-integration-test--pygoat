from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username='command-test', password='password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; touch /tmp/injected',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 400)
        mocked_popen.assert_not_called()
