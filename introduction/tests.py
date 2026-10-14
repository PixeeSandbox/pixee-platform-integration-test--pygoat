from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_authenticated_post_uses_argument_list(self, mock_popen, mock_render):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'example.com\n', b'')
        mock_popen.return_value = mock_process
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_malicious_domain_rejected_without_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('bad request')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
        self.assertEqual(response.status_code, 200)
