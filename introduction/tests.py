from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='password123',
        )

    def test_cmd_lab3_uses_argument_list_for_benign_hostname(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com  ', 'os': 'linux'})
        request.user = self.user

        popen_patcher = patch('introduction.other_views.subprocess.Popen')
        mock_process = popen_patcher.start()
        self.addCleanup(popen_patcher.stop)
        mock_process.return_value.communicate.return_value = (b'lookup ok', b'')

        response = cmd_lab3(request)

        self.assertEqual(mock_process.call_args.args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_process.call_args.kwargs)
        self.assertIn(b'lookup ok', response.content)

    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertIn(b'Invalid domain', response.content)
