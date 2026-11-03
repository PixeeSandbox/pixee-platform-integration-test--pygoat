import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_cmd_lab3_valid_post_uses_safe_subprocess_invocation(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render'
        ) as mock_render:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'lookup ok', b'')
            mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

            response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.content.decode(), 'lookup ok')

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render'
        ) as mock_render:
            mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content.decode(), 'Something went wrong')
