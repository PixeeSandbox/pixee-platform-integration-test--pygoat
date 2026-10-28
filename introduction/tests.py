from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_lookup(self):
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        process_mock = patch('introduction.views.subprocess.Popen')
        with process_mock as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup output', response.content)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))
