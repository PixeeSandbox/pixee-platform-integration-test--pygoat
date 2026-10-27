from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import ANY, Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_hostname_uses_argument_vector(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com', 'os': 'win'},
        )
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b'valid-output', b'')
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        mock_render.assert_called_once()
        self.assertEqual(response, mock_render.return_value)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_injected_domain_is_rejected_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; whoami', 'os': 'linux'},
        )
        request.user = self.user
        mock_render.return_value = Mock()

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'},
        )
        self.assertEqual(response, mock_render.return_value)
