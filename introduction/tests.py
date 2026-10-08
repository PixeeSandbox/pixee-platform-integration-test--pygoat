from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    def test_valid_hostname_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'lookup ok', b'')
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertIn(b'lookup ok', response.content)

    def test_malicious_domain_is_rejected_without_invoking_subprocess(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)
