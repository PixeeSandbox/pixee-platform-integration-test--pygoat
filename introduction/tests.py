from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch
from types import SimpleNamespace

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_list_arguments_for_valid_hostname(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_command_injection_payload(self, mock_popen):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
