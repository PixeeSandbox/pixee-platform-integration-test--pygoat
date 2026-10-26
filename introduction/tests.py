from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_valid_post_uses_argument_list_and_renders_output(self, mock_run):
        mock_run.return_value = Mock(stdout=b'command output\n', stderr=b'')
        request = self.factory.post('/cmd_lab', data={'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_run.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_run.call_args.kwargs)
        self.assertContains(response, 'command output')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab', data={'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
