from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username='tester')
        self.anonymous_user = AnonymousUser()

    def _post_request(self, data, authenticated=True):
        request = self.factory.post('/cmd_lab3', data)
        request.user = self.user if authenticated else self.anonymous_user
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen, mock_render):
        request = self._post_request({'domain': 'example.com; rm -rf /', 'os': 'win'})
        mock_render.return_value = 'rendered'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_argument_list_and_shell_false(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid', b'')
        request = self._post_request({'domain': 'example.com', 'os': 'win'})
        mock_render.return_value = 'rendered'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
