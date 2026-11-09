import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123'
        )

    def _render_response(self, request, template_name, context=None, *args, **kwargs):
        return HttpResponse(context.get('output', ''))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'answer', b'')
        mock_render.side_effect = self._render_response

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'answer')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = self._render_response

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Something went wrong')
        mock_popen.assert_not_called()
