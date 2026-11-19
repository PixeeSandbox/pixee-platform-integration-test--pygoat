from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd-lab/', {
            'domain': 'example.com;whoami',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = views.cmd_lab(request)

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)

    def test_cmd_lab_uses_shell_free_argument_list_for_valid_domain(self):
        request = self.factory.post('/cmd-lab/', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)
        with patch('introduction.views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'lookup output', b'')

            response = views.cmd_lab(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
