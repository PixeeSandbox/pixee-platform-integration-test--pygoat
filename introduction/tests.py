from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_cmd_lab(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return cmd_lab(request)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_command_injection_domain(self, popen):
        response = self.post_cmd_lab({'domain': 'example.com; touch /tmp/pwned', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_list_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'', b'')

        response = self.post_cmd_lab({'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)
