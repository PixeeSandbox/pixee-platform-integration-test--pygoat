from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_benign_hostname(self, mock_popen):
        process_mock = Mock()
        process_mock.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process_mock

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = Mock(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
