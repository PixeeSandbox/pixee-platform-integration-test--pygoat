from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import ANY, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_authenticated_post_uses_argument_list(self, mock_popen, mock_render):
        mock_process = SimpleNamespace(communicate=lambda: (b'ok', b''))
        mock_popen.return_value = mock_process
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertEqual(response.content, b'ok')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
        self.assertEqual(response.content, b'Something went wrong')
