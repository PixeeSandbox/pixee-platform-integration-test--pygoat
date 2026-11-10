from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_injection_like_hostname(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_executes_valid_hostname_as_argument(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'', b'')

        self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        args, kwargs = mock_popen.call_args
        self.assertEqual(args, (['nslookup', 'example.com'],))
        self.assertIs(kwargs['shell'], False)
