import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.render', return_value=HttpResponse('Something went wrong')) as mock_render, \
                patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.content, b'Something went wrong')
        mock_popen.assert_not_called()
        mock_render.assert_called_once()

    def test_cmd_lab3_uses_argument_list_without_shell_execution(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.render', return_value=HttpResponse('ok')) as mock_render, \
                patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_render.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
