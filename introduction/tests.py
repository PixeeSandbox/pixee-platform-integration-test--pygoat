from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
from django.http import HttpResponse

from introduction import other_views
from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='password123'
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('rendered response')

        request = self.factory.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], other_views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], other_views.subprocess.PIPE)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookup output'}
        )
        self.assertEqual(response.content, b'rendered response')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')

        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; id',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
        self.assertEqual(response.content, b'Something went wrong')
