from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')

        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'example output', response.content)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell'))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        mock_popen.assert_not_called()
