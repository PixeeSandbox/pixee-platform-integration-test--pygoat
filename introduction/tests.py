import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_host_uses_fixed_executable_and_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        for os_choice, executable in [('win', 'nslookup'), ('linux', 'dig')]:
            with self.subTest(os_choice=os_choice):
                response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': os_choice})

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, 'example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                popen.reset_mock()

    @patch('introduction.views.subprocess.Popen')
    def test_invalid_host_is_rejected_without_running_command(self, popen):
        invalid_hosts = [None, '', '   ', 'example.com; touch /tmp/pwned', 'example.com/path', 'bad..example']

        for domain in invalid_hosts:
            with self.subTest(domain=domain):
                data = {'os': 'linux'}
                if domain is not None:
                    data['domain'] = domain
                response = self.client.post('/cmd_lab', data)

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
                self.assertEqual(response.context['output'], 'Invalid hostname')
                popen.assert_not_called()
