from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CommandInjectionTests(TestCase):
    def test_cmd_lab_rejects_shell_syntax_without_execution(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as process_mock:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        process_mock.assert_not_called()
