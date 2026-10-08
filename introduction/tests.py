from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3, is_valid_domain


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_input(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('safe error')
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertFalse(mock_run.called)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertEqual(response.content, b'safe error')

    def test_is_valid_domain_accepts_normal_hostname(self):
        self.assertTrue(is_valid_domain('example.com'))
        self.assertFalse(is_valid_domain('example.com;rm -rf /'))
