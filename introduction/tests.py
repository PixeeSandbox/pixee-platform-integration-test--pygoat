from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])
        request = self.factory.post('/cmd_lab3/', {
            'domain': 'example.com; whoami',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_valid_domain(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'result', b'')
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])
        request = self.factory.post('/cmd_lab3/', {
            'domain': 'https://www.Example.COM',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'result')
