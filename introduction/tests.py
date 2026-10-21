from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import MagicMock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab_rejects_malicious_domain_without_popen(self):
        request = self.factory.post('/cmd_lab', {'domain': 'google.com; id', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.google.com', 'os': 'linux'})
        request.user = self.user

        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'google.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertContains(response, 'lookup ok')
