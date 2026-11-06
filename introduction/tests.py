from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='cmdlabuser',
            email='cmdlabuser@example.com',
            password='StrongPassword123!'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_input(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain name')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_without_shell_for_valid_domain(self, mock_popen):
        self.client.force_login(self.user)
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'lookup ok', b'')

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertContains(response, 'lookup ok')
