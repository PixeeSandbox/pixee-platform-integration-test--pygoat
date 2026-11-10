from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com;whoami',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_runs_fixed_executable_with_domain_as_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
