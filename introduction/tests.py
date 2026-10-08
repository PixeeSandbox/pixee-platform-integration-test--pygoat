from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    def test_cmd_lab_uses_argument_list_and_disables_shell(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'lookup ok', b'')

            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('lookup ok', response.content.decode())
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])

    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())
        mock_popen.assert_not_called()
