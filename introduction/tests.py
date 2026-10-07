from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_cmd_lab_rejects_malicious_domain_without_shell_execution(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; whoami',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'lookup output', b'')

            response = self.client.post('/cmd_lab', {
                'domain': 'example.com',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'lookup output')
