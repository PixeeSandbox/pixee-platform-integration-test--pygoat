from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; rm -rf /',
            'os': 'win',
        })
        request.user = self.user

        with patch('introduction.other_views.render', return_value=MagicMock()) as mock_render, \
                patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertIs(response, mock_render.return_value)

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = self.user

        process = MagicMock()
        process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.render', return_value=MagicMock()) as mock_render, \
                patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertIs(response, mock_render.return_value)
