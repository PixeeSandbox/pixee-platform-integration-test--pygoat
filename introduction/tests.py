from types import SimpleNamespace
from unittest.mock import patch
import subprocess

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def test_cmd_lab_valid_domain_uses_argument_list(self):
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com/', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.render', side_effect=lambda request, template_name, context=None: HttpResponse(context.get('output', ''))), patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'answer', b'')

            response = cmd_lab(request)

        mock_popen.assert_called_once_with(['nslookup', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(response.content, b'answer')

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.render', side_effect=lambda request, template_name, context=None: HttpResponse(context.get('output', ''))) as mock_render, patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.content, b'Invalid domain')
