import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertEqual(response, mock_render.return_value)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'dns ok', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
