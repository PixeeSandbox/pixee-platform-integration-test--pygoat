from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='secret123',
        )

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_valid_domain_uses_argument_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout='lookup ok\n', stderr='')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_run.call_args.kwargs)
        self.assertIn('lookup ok', response.content.decode())

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertIn('Something went wrong', response.content.decode())
