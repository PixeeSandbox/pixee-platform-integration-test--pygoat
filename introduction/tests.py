from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='secure-password-123',
        )
        self.client = Client()
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'example.com; cat /etc/passwd',
                'os': 'win',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertEqual(response.context['output'], 'Something went wrong')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_and_disables_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'example.com',
                'os': 'win',
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', True))
        self.assertEqual(response.context['output'], 'lookup output')
