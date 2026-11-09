from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'benign output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'benign output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com && id', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
