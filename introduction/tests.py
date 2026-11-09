from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch
import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_rejects_malicious_domain_without_popen(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as popen_mock, patch('introduction.other_views.render', return_value=HttpResponse('bad request')) as render_mock:
            response = cmd_lab3(request)

        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertEqual(response.content, b'bad request')

    def test_valid_hostname_uses_argument_list_and_no_shell(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen_mock, patch('introduction.other_views.render', return_value=HttpResponse('ok')) as render_mock:
            response = cmd_lab3(request)

        popen_mock.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotIn('shell', popen_mock.call_args.kwargs)
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'example output'})
        self.assertEqual(response.content, b'ok')
