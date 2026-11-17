from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def authenticated_post(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = type('User', (), {'is_authenticated': True})()
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_injection(self, popen, render):
        response = other_views.cmd_lab3(self.authenticated_post({
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        }))

        self.assertEqual(response, render.return_value)
        render.assert_called_once()
        popen.assert_not_called()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_runs_valid_hostname_without_shell(self, popen, render):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = other_views.cmd_lab3(self.authenticated_post({
            'domain': 'https://www.example.com',
            'os': 'win',
        }))

        self.assertEqual(response, render.return_value)
        popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
