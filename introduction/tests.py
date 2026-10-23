import subprocess

from django.test import TestCase, RequestFactory
from unittest.mock import patch, Mock

from django.contrib.auth.models import User

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username='testuser')

    def test_cmd_lab_uses_argument_list_without_shell(self):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'win'}
        )
        request.user = self.user

        process_mock = Mock()
        process_mock.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process_mock) as popen_mock:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com; rm -rf /'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
