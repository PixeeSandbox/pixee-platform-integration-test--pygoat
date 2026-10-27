from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.render')
    def test_cmd_lab_rejects_malicious_domain(self, mock_render, mock_popen):
        mock_render.return_value = HttpResponse('blocked')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.content, b'blocked')
