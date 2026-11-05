from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch
from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_and_disables_shell_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
