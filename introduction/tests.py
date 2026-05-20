from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import _normalize_cmd_domain, cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd-user',
            password='password123',
        )

    def test_normalize_cmd_domain_allows_only_safe_inputs(self):
        self.assertEqual(_normalize_cmd_domain('https://www.Example.com'), 'example.com')
        self.assertEqual(_normalize_cmd_domain('example.com:53'), 'example.com')
        self.assertEqual(_normalize_cmd_domain('192.168.0.1'), '192.168.0.1')
        self.assertEqual(_normalize_cmd_domain('sub.example.co.uk'), 'sub.example.co.uk')
        self.assertEqual(_normalize_cmd_domain('https://example.com/'), 'example.com')

    def test_normalize_cmd_domain_rejects_shell_metacharacters_and_paths(self):
        for value in [
            'example.com;id',
            'example.com && id',
            'example.com|id',
            'example.com\nid',
            'example.com id',
            'example.com\tid',
            'https://example.com/path',
            'https://example.com?x=1',
            'example.com%0aid',
            '256.256.256.256',
            '-bad.example.com',
            'bad-.example.com',
            'example.com:70000',
        ]:
            self.assertEqual(_normalize_cmd_domain(value), '')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_and_respects_os_branching(self, mock_run):
        mock_run.return_value = MagicMock(stdout='ok', stderr='')

        for os_value, executable in [('win', 'nslookup'), ('linux', 'dig')]:
            request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': os_value})
            request.user = self.user

            response = cmd_lab(request)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(mock_run.call_args.args[0], [executable, 'example.com'])
            self.assertNotIn('shell', mock_run.call_args.kwargs)
            self.assertTrue(mock_run.call_args.kwargs['text'])
            self.assertFalse(mock_run.call_args.kwargs['check'])
            mock_run.reset_mock()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_invalid_domain_before_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
