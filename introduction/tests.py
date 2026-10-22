from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth.models import User


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='Password123!')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell_for_benign_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(response.context['output'], 'lookup output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_payloads_before_subprocess(self, mock_popen):
        for payload in ['https://www.example.com;id', 'example.com && id', 'example.com|id', 'example.com$(id)']:
            with self.subTest(payload=payload):
                response = self.client.post(
                    '/cmd_lab',
                    {'domain': payload, 'os': 'win'}
                )

                self.assertEqual(response.status_code, 200)
                mock_popen.assert_not_called()
                self.assertEqual(response.context['output'], 'Something went wrong')
                mock_popen.reset_mock()
