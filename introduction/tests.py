from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_fixed_subprocess_arguments(self, mock_run):
        mock_run.return_value = Mock(stdout='example.com.\tIN\tA\t93.184.216.34\n', stderr='')
        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertTrue(kwargs['capture_output'])
        self.assertTrue(kwargs['text'])
        self.assertIn(b'example.com.\tIN\tA\t93.184.216.34', response.content)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertIn(b'Invalid domain', response.content)
