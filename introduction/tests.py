from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Something went wrong')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        cmd_lab3(request)

        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
