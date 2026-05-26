import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import _is_valid_cmd_domain, cmd_lab


class CmdLabValidationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username='tester')

    def test_domain_helper_accepts_hostname_and_https_prefix(self):
        self.assertEqual(_is_valid_cmd_domain('example.com'), 'example.com')
        self.assertEqual(_is_valid_cmd_domain('https://www.example.com'), 'example.com')
        self.assertEqual(_is_valid_cmd_domain('203.0.113.10'), '203.0.113.10')

    def test_domain_helper_rejects_paths_queries_and_shell_metacharacters(self):
        self.assertIsNone(_is_valid_cmd_domain('example.com/path'))
        self.assertIsNone(_is_valid_cmd_domain('example.com?x=1'))
        self.assertIsNone(_is_valid_cmd_domain('http://example.com'))
        self.assertIsNone(_is_valid_cmd_domain('example.com;rm -rf /'))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content.decode(), 'output')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab', {'domain': 'example.com/path', 'os': 'lin'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content.decode(), 'Something went wrong')
        mock_popen.assert_not_called()
