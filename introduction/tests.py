from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import views


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPassword123!'
        )

    def _mock_render(self, request, template_name, context=None, *args, **kwargs):
        return HttpResponse(str(context or {}))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_normal_domain(self, mock_popen, mock_render):
        mock_render.side_effect = self._mock_render
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com', 'os': 'linux'}
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.content.decode(), "{'output': 'example output'}")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen, mock_render):
        mock_render.side_effect = self._mock_render

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertIn('Something went wrong', response.content.decode())
