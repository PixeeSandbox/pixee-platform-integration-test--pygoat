import subprocess
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_blocks_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user
        mock_render.return_value = Mock()

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
        self.assertEqual(response, mock_render.return_value)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        request = self.factory.post(
            '/cmd_lab/',
            data={'domain': 'example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'output'},
        )
        self.assertEqual(response, mock_render.return_value)
