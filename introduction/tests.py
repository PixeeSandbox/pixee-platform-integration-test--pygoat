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
            username='tester',
            password='password123'
        )

    def test_valid_domain_uses_argv_list_without_shell(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, \
                patch('introduction.other_views.render', return_value=HttpResponse('ok')) as mock_render:
            process = mock_popen.return_value
            process.communicate.return_value = (b'example output', b'')

            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], subprocess.PIPE)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'example output'}
        )

    def test_malicious_domain_is_rejected_before_subprocess(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, \
                patch('introduction.other_views.render', return_value=HttpResponse('ok')) as mock_render:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'}
        )
