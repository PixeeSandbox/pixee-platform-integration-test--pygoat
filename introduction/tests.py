from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_and_shell_false(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        mock_process = patch('introduction.other_views.subprocess.Popen').start()
        self.addCleanup(patch.stopall)
        mock_process.return_value.communicate.return_value = (b'lookup ok', b'')

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_process.assert_called_once()
        args, kwargs = mock_process.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
