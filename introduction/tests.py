from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='cmduser', password='cmdpassword123')
        self.client = Client()
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell_for_valid_domain(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b'valid output', b'')
        popen_mock.return_value = process

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertIn('valid output', response.content.decode())

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_subprocess_execution(self, popen_mock):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_not_called()
        self.assertIn('Something went wrong', response.content.decode())
