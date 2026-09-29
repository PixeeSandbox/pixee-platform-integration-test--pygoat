from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpass123',
        )

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_before_spawning_process(self, mock_run):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(mock_run.call_count, 0)
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_list_arguments_without_shell(self, mock_run):
        mock_run.return_value = Mock(stdout='lookup output', stderr='')
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertTrue(kwargs.get('capture_output'))
        self.assertTrue(kwargs.get('text'))
        self.assertContains(response, 'lookup output')
