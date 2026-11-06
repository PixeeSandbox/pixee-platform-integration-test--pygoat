import subprocess

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; whoami', 'os': 'win'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render',
            side_effect=lambda request, template, context: HttpResponse(context['output']),
        ):
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com', 'os': 'win'},
        )
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen, patch(
            'introduction.other_views.render',
            side_effect=lambda request, template, context: HttpResponse(context['output']),
        ):
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
