from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123'
        )

    def _build_request(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab3/', data={'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'lookup output', b'')
        mock_render.return_value = HttpResponse('rendered')

        request = self._build_request('example.com')
        response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookup output'}
        )
        self.assertEqual(response.content, b'rendered')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injection_payload(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rendered')

        request = self._build_request('example.com; id')
        response = other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
        self.assertEqual(response.content, b'rendered')
