import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab, is_valid_cmd_domain


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd-user',
            password='test-password',
        )

    def _request(self, domain, os_value):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    def test_validation_accepts_hostname_and_ip_literal(self):
        self.assertTrue(is_valid_cmd_domain('example.com'))
        self.assertTrue(is_valid_cmd_domain('127.0.0.1'))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_argument_list_for_windows_lookup(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'OK', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context=None: HttpResponse(json.dumps(context or {}))

        response = cmd_lab(self._request('https://www.example.com', 'win'))

        self.assertEqual(response.content.decode(), '{"output": "OK"}')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_argument_list_for_dig(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'OK', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context=None: HttpResponse(json.dumps(context or {}))

        response = cmd_lab(self._request('127.0.0.1', 'linux'))

        self.assertEqual(response.content.decode(), '{"output": "OK"}')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', '127.0.0.1'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_payloads_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context=None: HttpResponse(json.dumps(context or {}))

        for payload in ('example.com; id', 'example.com with space', 'example.com|id', 'example.com/id', ''):
            with self.subTest(payload=payload):
                response = cmd_lab(self._request(payload, 'win'))
                self.assertEqual(response.content.decode(), '{"output": "Something went wrong"}')
                mock_popen.assert_not_called()
                self.assertEqual(mock_render.call_args[0][2], {'output': 'Something went wrong'})
                mock_render.reset_mock()
