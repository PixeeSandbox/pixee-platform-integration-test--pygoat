from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.login(username='testuser', password='testpass123')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout='resolved\n', stderr='')

        response = self.client.post('/cmd_lab', {
            'domain': 'https://www.example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertTrue(kwargs['capture_output'])
        self.assertTrue(kwargs['text'])
        self.assertContains(response, 'resolved')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_injected_domain_without_invoking_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab', {
            'domain': 'https://www.example.com; rm -rf /',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
