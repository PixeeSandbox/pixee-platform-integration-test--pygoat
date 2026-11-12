from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_hostname_uses_fixed_executable_without_shell(self, popen):
        popen.return_value.communicate.return_value = (b'output', b'')

        for os_choice, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_choice):
                self.client.post('/cmd_lab', {'domain': 'example.com', 'os': os_choice})
                args, kwargs = popen.call_args
                self.assertEqual(args[0], [executable, 'example.com'])
                self.assertFalse(kwargs.get('shell', False))

    @patch('introduction.views.subprocess.Popen')
    def test_invalid_hostname_does_not_execute_subprocess(self, popen):
        self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})

        popen.assert_not_called()
