from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse('blocked')
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
        self.assertEqual(response.content, b'blocked')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, popen_mock, render_mock):
        process = MagicMock()
        process.communicate.return_value = (b'resolved', b'')
        popen_mock.return_value = process
        render_mock.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        popen_mock.assert_called_once()
        call_args, call_kwargs = popen_mock.call_args
        self.assertEqual(call_args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', call_kwargs)
        self.assertEqual(call_kwargs['stdout'], other_views.subprocess.PIPE)
        self.assertEqual(call_kwargs['stderr'], other_views.subprocess.PIPE)
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'resolved'},
        )
        self.assertEqual(response.content, b'ok')
