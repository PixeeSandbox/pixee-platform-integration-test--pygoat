from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            email='tester@example.com',
            password='test-password',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('blocked')
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com; whoami', 'os': 'win'},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b'blocked')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_and_shell_false(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'answer', b'')
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], other_views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], other_views.subprocess.PIPE)
        self.assertEqual(process.communicate.call_count, 1)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'answer'},
        )
