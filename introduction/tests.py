from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_safe_argument_list_for_benign_domain(self, mock_run, mock_render):
        mock_run.return_value = Mock(stdout='lookup result', stderr='')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)
        self.assertEqual(response.content, b'ok')
        self.assertEqual(mock_render.call_args.args[2]['output'], 'lookup result')

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters_before_subprocess(self, mock_run, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = Mock(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.content, b'ok')
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Something went wrong')
