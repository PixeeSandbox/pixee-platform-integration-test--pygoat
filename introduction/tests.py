from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='password1234'
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertEqual(response.content.decode(), 'Something went wrong')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = ('lookup output', 'lookup error')
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertTrue(kwargs['stdout'])
        self.assertTrue(kwargs['stderr'])
        self.assertTrue(kwargs['text'])
        self.assertEqual(response.content.decode(), 'lookup outputlookup error')
