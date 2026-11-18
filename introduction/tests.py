from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_passes_valid_hostname_as_argument(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'www.example.com', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()
        with patch('introduction.views.subprocess.Popen') as process:
            process.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        process.assert_called_once()
        args, kwargs = process.call_args
        self.assertEqual(args[0], ['nslookup', 'www.example.com'])
        self.assertIs(kwargs['shell'], False)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()

        with patch('introduction.views.subprocess.Popen') as process:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        process.assert_not_called()
