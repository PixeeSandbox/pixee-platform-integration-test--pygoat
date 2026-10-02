from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain(self, run_mock, render_mock):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;rm -rf /', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        render_mock.return_value = HttpResponse('invalid')

        response = cmd_lab3(request)

        run_mock.assert_not_called()
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertEqual(response.content, b'invalid')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_safe_argument_list(self, run_mock, render_mock):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)
        run_mock.return_value = SimpleNamespace(stdout='dns output', stderr='')
        render_mock.return_value = HttpResponse('valid')

        response = cmd_lab3(request)

        run_mock.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'dns output'})
        self.assertEqual(response.content, b'valid')
