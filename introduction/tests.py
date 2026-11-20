from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_hostname_uses_safe_arguments(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'output', b'')
        request = self.factory.post('/cmd/', {'domain': 'example.com', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()

        other_views.cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_invalid_hostname(self, mock_popen):
        request = self.factory.post('/cmd/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()

        other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
