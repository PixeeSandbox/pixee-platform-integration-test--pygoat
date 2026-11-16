from unittest.mock import Mock, patch
from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_lookup(self, domain, os='win'):
        request = self.factory.post('/cmd_lab3', {'domain': domain, 'os': os})
        request.user = SimpleNamespace(is_authenticated=True)
        return other_views.cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, popen):
        response = self.post_lookup('example.com; touch /tmp/pwned')

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_shell_free_argument_list(self, popen):
        process = Mock()
        process.communicate.return_value = (b'lookup result', b'')
        popen.return_value = process

        response = self.post_lookup('www.example.com', os='win')

        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        process.communicate.assert_called_once_with()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup result')
