from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    def _render(self, request, template_name, context=None, *args, **kwargs):
        return HttpResponse((context or {}).get('output', ''))

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_post_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'valid output', b'')
        mock_popen.return_value = process
        mock_render.side_effect = self._render

        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=-1,
            stderr=-1,
        )
        self.assertEqual(response.content.decode(), 'valid output')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = self._render

        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content.decode(), 'Something went wrong')
