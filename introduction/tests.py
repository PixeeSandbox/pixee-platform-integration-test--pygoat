from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import ANY, patch


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_injection_hostname(self, popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
