from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_valid_hostname_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab3(request)

        self.assertTrue(mock_popen.called)
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertIn(b'lookup ok', response.content)

    def test_malicious_hostname_is_rejected_without_subprocess(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)
