from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_popen, mock_render):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = mock_process
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = MagicMock(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookup ok'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('invalid')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;rm -rf /', 'os': 'win'})
        request.user = MagicMock(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'invalid')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'},
        )
