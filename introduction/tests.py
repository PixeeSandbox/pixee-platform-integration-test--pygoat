from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='alice',
            password='password123',
        )

    def _build_request(self, domain, os_value='win'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.views.render', return_value=HttpResponse('ok'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        response = views.cmd_lab(self._build_request('example.com', 'win'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(mock_render.call_args.args[2]['output'], 'lookup output')

    @patch('introduction.views.render', return_value=HttpResponse('ok'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_execution(self, mock_popen, mock_render):
        response = views.cmd_lab(self._build_request('example.com; rm -rf /', 'win'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Something went wrong')
