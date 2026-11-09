from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='tester',
            password='password123'
        )

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_list_based_popen_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertEqual(kwargs['stdout'], other_views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], other_views.subprocess.PIPE)
        self.assertNotIn('shell', kwargs)
        mock_render.assert_called_once()

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; rm -rf /', 'os': 'win'}
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(
            mock_render.call_args.args[2],
            {'output': 'Something went wrong'}
        )
