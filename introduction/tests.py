from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    def render_stub(self, request, template_name, context=None, *args, **kwargs):
        context = context or {}
        return HttpResponse(context.get('output', ''))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_domain_uses_argument_list(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'nslookup output', b'')
        popen_mock.return_value = process
        render_mock.side_effect = self.render_stub

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'nslookup output')
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], views.subprocess.PIPE)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injection_payload(self, popen_mock, render_mock):
        render_mock.side_effect = self.render_stub

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        popen_mock.assert_not_called()
