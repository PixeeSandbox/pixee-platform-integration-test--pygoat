from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_metacharacters_without_running_process(self, popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')

    @patch('introduction.views.subprocess.Popen')
    def test_runs_valid_hostname_without_shell(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'answer', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'answer')
