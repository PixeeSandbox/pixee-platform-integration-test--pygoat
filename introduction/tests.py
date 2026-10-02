from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import ANY, Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, data):
        request = self.factory.post('/cmd_lab3', data=data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_without_executing_command(self, popen_mock, render_mock):
        render_mock.side_effect = lambda request, template, context: {
            'template': template,
            'context': context,
        }

        request = self._authenticated_post({'domain': 'example.com; rm -rf /', 'os': 'linux'})
        response = cmd_lab3(request)

        popen_mock.assert_not_called()
        self.assertEqual(response['context']['output'], 'Invalid domain')
        render_mock.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_argv_and_returns_command_output(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'lookup ok\n', b'')
        popen_mock.return_value = process
        render_mock.side_effect = lambda request, template, context: {
            'template': template,
            'context': context,
        }

        request = self._authenticated_post({'domain': 'https://www.example.com', 'os': 'linux'})
        response = cmd_lab3(request)

        popen_mock.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertEqual(response['context']['output'], 'lookup ok\n')
        self.assertEqual(response['template'], 'Lab/CMD/cmd_lab.html')
