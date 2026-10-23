from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester', password='password123'
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_safe_domain(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'safe output', b'')
        mock_popen.return_value = process
        mock_render.side_effect = (
            lambda request, template, context=None, *args, **kwargs: HttpResponse(
                context.get('output', '')
            )
        )

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com', 'os': 'linux'}
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.content, b'safe output')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_popen(self, mock_popen, mock_render):
        mock_render.side_effect = (
            lambda request, template, context=None, *args, **kwargs: HttpResponse(
                context.get('output', '')
            )
        )

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content, b'Something went wrong')
