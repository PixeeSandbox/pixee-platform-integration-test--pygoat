from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='testpass123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        mock_render.return_value = HttpResponse('rendered')

        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injection_like_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rendered')

        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com;rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Something went wrong')
