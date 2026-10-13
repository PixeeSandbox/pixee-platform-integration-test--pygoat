from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def _build_request(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self):
        process_mock = Mock()
        process_mock.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process_mock) as popen_mock, patch('introduction.other_views.render') as render_mock:
            render_mock.return_value = HttpResponse('ok')
            response = cmd_lab3(self._build_request('example.com'))

        self.assertEqual(response.content, b'ok')
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]['output'], 'lookup ok')

    def test_cmd_lab3_rejects_injected_payload_before_subprocess(self):
        with patch('introduction.other_views.subprocess.Popen') as popen_mock, patch('introduction.other_views.render') as render_mock:
            render_mock.return_value = HttpResponse('invalid')
            response = cmd_lab3(self._build_request('example.com;id'))

        self.assertEqual(response.content, b'invalid')
        popen_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]['output'], 'Invalid domain')
