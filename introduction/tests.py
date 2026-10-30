from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='cmduser', password='password123')
        self.client.login(username='cmduser', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'good', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
