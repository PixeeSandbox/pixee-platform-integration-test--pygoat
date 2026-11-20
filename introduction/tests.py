from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')

    def post_cmd_lab(self, domain, os='win'):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os})
        request.user = self.user
        return views.cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_shell_syntax_without_launching_subprocess(self, mock_popen):
        response = self.post_cmd_lab('example.com; whoami')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        self.post_cmd_lab('www.example.com', os='win')

        mock_popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
