import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='safe-password-123',
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_dns_lookup_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(
            context['output']
        )

        request = self.factory.post('/cmd_lab', data={'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'example output')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIsInstance(mock_popen.call_args.args[0], list)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_malicious_payload_is_rejected_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(
            context['output']
        )

        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com;whoami', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Something went wrong')
        mock_popen.assert_not_called()
