from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlabuser', password='password123')

    def test_rejects_malicious_domain_without_popen(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)

    def test_uses_argument_list_and_disables_shell(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b'valid output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertIn(b'valid output', response.content)
