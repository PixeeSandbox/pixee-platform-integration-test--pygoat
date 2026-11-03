from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertFalse(mock_popen.called)
        self.assertContains(response, 'Something went wrong')

    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'valid output', b'')
            response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'valid output')
