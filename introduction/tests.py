import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.render') as mock_render, patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'example output', b'')
            mock_render.return_value = HttpResponse('ok')

            response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'example output'})
        self.assertEqual(response.status_code, 200)

    def test_cmd_lab3_rejects_malicious_domain_before_execution(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.render') as mock_render, patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_render.return_value = HttpResponse('invalid')

            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})
        self.assertEqual(response.status_code, 200)
