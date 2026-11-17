from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.render', return_value=HttpResponse())
    def test_rejects_domain_with_shell_metacharacters(self, mock_render, mock_popen):
        self.post_cmd_lab({'domain': 'example.com; whoami', 'os': 'linux'})

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Invalid domain')

    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.render', return_value=HttpResponse())
    def test_valid_hostname_uses_argument_list_without_shell(self, mock_render, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post_cmd_lab({'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
