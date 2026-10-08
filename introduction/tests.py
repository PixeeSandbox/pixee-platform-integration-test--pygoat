from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='safe-password-123'
        )

    def test_cmd_lab_uses_argument_list_without_shell_for_safe_domain(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as process_mock:
            process_mock.return_value.communicate.return_value = (b'output', b'')

            response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        process_mock.assert_called_once()
        args, kwargs = process_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))

    def test_cmd_lab_rejects_malicious_domain_before_subprocess_call(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'https://www.example.com;rm -rf /', 'os': 'win'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
