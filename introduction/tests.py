from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_input(self, mock_run):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'win'}
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain input', response.content)
        mock_run.assert_not_called()
