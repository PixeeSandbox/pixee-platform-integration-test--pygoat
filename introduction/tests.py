from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from . import views


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='StrongPassword123!'
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com;whoami', 'os': 'linux'}
        )
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
        self.assertEqual(response.content, b'Something went wrong')
