from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabSecurityTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        mock_popen.assert_not_called()
