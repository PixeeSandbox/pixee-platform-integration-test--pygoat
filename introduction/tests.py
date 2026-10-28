from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views, views


class CommandInjectionFixTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, popen_mock, render_mock):
        process_mock = popen_mock.return_value
        process_mock.communicate.return_value = (b'nslookup output', b'')
        render_mock.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], other_views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], other_views.subprocess.PIPE)
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'nslookup output'}
        )
        self.assertEqual(response.content, b'ok')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse('blocked')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;whoami', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
        self.assertEqual(response.content, b'blocked')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, popen_mock, render_mock):
        process_mock = popen_mock.return_value
        process_mock.communicate.return_value = (b'dig output', b'')
        render_mock.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab/', {'domain': 'example.org', 'os': 'linux'})
        request.user = self.user

        response = views.cmd_lab(request)

        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['dig', 'example.org'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], views.subprocess.PIPE)
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'dig output'}
        )
        self.assertEqual(response.content, b'ok')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse('blocked')

        request = self.factory.post('/cmd_lab/', {'domain': 'example.org && id', 'os': 'linux'})
        request.user = self.user

        response = views.cmd_lab(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
        self.assertEqual(response.content, b'blocked')
