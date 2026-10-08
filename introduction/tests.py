from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='tester', password='password123')

    def _make_request(self, domain, os_value='linux'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, popen_mock, render_mock):
        render_mock.side_effect = lambda request, template, context: HttpResponse(context['output'])
        request = self._make_request('example.com; rm -rf /', 'linux')

        response = cmd_lab3(request)

        popen_mock.assert_not_called()
        self.assertEqual(response.content, b'Something went wrong')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        popen_mock.return_value = process
        render_mock.side_effect = lambda request, template, context: HttpResponse(context['output'])
        request = self._make_request('example.com', 'win')

        response = cmd_lab3(request)

        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(response.content, b'lookup ok')
