import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password',
        )

    def _make_request(self, domain, os_name):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_name})
        request.user = self.user
        return request

    @patch('introduction.other_views.render', return_value=None)
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_nslookup_argv_for_windows(self, mock_run, mock_render):
        mock_run.return_value.stdout = 'lookup output'
        mock_run.return_value.stderr = 'lookup error'

        cmd_lab3(self._make_request('https://www.example.com', 'win'))

        self.assertEqual(mock_run.call_args.args[0], ['nslookup', 'example.com'])
        self.assertEqual(mock_run.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_run.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertTrue(mock_run.call_args.kwargs['text'])

    @patch('introduction.other_views.render', return_value=None)
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_dig_argv_for_non_windows(self, mock_run, mock_render):
        mock_run.return_value.stdout = 'lookup output'
        mock_run.return_value.stderr = 'lookup error'

        cmd_lab3(self._make_request('https://www.example.com', 'linux'))

        self.assertEqual(mock_run.call_args.args[0], ['dig', 'example.com'])
        self.assertEqual(mock_run.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(mock_run.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertTrue(mock_run.call_args.kwargs['text'])
