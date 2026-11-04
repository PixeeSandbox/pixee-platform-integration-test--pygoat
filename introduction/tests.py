from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'https://www.example.com',
            'os': 'win',
        })
        request.user = self.user

        process_mock = MagicMock()
        process_mock.communicate.return_value = (b'example output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process_mock) as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['nslookup', 'example.com'])
        self.assertTrue('shell' not in called_kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'example output', response.content)

    def test_cmd_lab3_rejects_malicious_domain_without_calling_subprocess(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
