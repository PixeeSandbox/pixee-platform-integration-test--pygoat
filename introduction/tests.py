from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_runs_lookup_with_separate_arguments(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
