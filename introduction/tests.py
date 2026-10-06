from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )

    def _render_response(self, request, template_name, context):
        return HttpResponse(context['output'])

    @patch('introduction.other_views.subprocess.run')
    @patch('introduction.other_views.render')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_render, mock_run):
        mock_render.side_effect = self._render_response
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com;id', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.content.decode(), 'Something went wrong')

    @patch('introduction.other_views.subprocess.run')
    @patch('introduction.other_views.render')
    def test_cmd_lab3_uses_argv_list_for_valid_domain(self, mock_render, mock_run):
        mock_render.side_effect = self._render_response
        mock_run.return_value = type('CompletedProcess', (), {
            'stdout': 'ok\n',
            'stderr': '',
        })()
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(response.content.decode(), 'ok\n')
