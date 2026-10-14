import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd_tester',
            password='password123',
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_unsafe_domain_without_invoking_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab', data={'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_shell_false_for_valid_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('ok')
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')
        request = self.factory.post('/cmd_lab', data={'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'example output'},
        )
        self.assertEqual(response.status_code, 200)
