import subprocess

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'answer', b'')

        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'example.com; id', 'os': 'linux'}
        )
        request.user = self.user

        from introduction.views import cmd_lab

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0], ['dig', 'example.com; id'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
