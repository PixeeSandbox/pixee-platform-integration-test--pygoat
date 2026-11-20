from unittest.mock import call, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_fixed_executable_and_separate_argument(self, popen, render):
        process = popen.return_value
        process.communicate.return_value = (b'lookup result', b'')

        for os_selection in ('win', 'linux'):
            request = self.factory.post('/', {'domain': 'https://www.example.com', 'os': os_selection})
            request.user = self.user

            views.cmd_lab(request)

        self.assertEqual(
            popen.call_args_list,
            [
                call(
                    ['nslookup', 'example.com'],
                    shell=False,
                    stdout=views.subprocess.PIPE,
                    stderr=views.subprocess.PIPE,
                ),
                call(
                    ['dig', 'example.com'],
                    shell=False,
                    stdout=views.subprocess.PIPE,
                    stderr=views.subprocess.PIPE,
                ),
            ],
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_domain_with_shell_metacharacters_is_rejected(self, popen, render):
        request = self.factory.post('/', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user

        views.cmd_lab(request)

        popen.assert_not_called()
        render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
