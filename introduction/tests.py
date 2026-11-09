from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import Mock, patch
from django.http import HttpResponse

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, popen_mock, render_mock):
        request = self.factory.post('/cmd_lab3', data={'domain': 'example.com; whoami', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        render_mock.return_value = HttpResponse('Invalid domain')

        response = other_views.cmd_lab3(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})
        self.assertEqual(response.content, b'Invalid domain')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_list_invocation_for_valid_domain(self, popen_mock, render_mock):
        request = self.factory.post('/cmd_lab3', data={'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        process = SimpleNamespace(communicate=Mock(return_value=(b'lookup ok', b'')))
        popen_mock.return_value = process
        render_mock.return_value = HttpResponse('lookup ok')

        response = other_views.cmd_lab3(request)

        popen_mock.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'lookup ok'})
        self.assertEqual(response.content, b'lookup ok')
