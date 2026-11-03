from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123'
        )

    def test_cmd_lab_rejects_malicious_domain_without_popen(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_popen_with_argument_list_and_shell_false(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'lookup ok', b'')
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args[1]['shell'])
