from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_shell_metacharacters(self, mock_popen, mock_render):
        self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})

        mock_popen.assert_not_called()

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_invokes_lookup_with_hostname_without_shell(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'example.com', b'')

        self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)
        self.assertIn('stdout', kwargs)
        self.assertIn('stderr', kwargs)
