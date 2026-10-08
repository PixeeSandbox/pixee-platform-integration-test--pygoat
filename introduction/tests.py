from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def test_cmd_lab3_uses_argument_list_for_unix_branch(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render', return_value=HttpResponse('ok')
        ) as mock_render:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'stdout', b'stderr')

            response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'stdoutstderr'},
        )

    def test_cmd_lab3_uses_argument_list_for_windows_branch(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render', return_value=HttpResponse('ok')
        ) as mock_render:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'stdout', b'stderr')

            response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'stdoutstderr'},
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post(
            '/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render', return_value=HttpResponse('blocked')
        ) as mock_render:
            response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b'blocked')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
