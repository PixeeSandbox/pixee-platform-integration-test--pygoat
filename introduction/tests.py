import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain input')
        self.assertNotContains(response, 'nslookup ')
        self.assertNotContains(response, 'dig ')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        mock_process = SimpleNamespace(
            communicate=lambda: (b'lookup output', b''),
        )

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertEqual(mock_popen.call_args.kwargs, {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        })
