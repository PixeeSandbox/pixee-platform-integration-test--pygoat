from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='pass12345')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup ok', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
