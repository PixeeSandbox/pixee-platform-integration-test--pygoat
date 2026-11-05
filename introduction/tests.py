from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd_user',
            password='safe-password-123',
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com;id', 'os': 'win'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com', 'os': 'win'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'lookup ok', b'')
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertIn('lookup ok', response.content.decode())
