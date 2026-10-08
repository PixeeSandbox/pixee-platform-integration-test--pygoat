from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_valid_domain_uses_argument_list(self, mock_run):
        mock_run.return_value = type('Result', (), {'stdout': 'dns ok', 'stderr': ''})()
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_run.called)
        self.assertContains(response, 'Something went wrong')
