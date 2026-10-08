from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_before_execution(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com;rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertFalse(mock_popen.called)

    def test_cmd_lab3_uses_argument_list_and_no_shell_for_valid_domain(self):
        process = Mock()
        process.communicate.return_value = (b'stdout', b'stderr')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'stdoutstderr')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
