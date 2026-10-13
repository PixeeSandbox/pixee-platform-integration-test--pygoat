from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab_rejects_malicious_domain_input(self):
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com;id', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()
