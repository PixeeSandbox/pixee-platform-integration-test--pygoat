from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3
from introduction.views import cmd_lab


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.views.subprocess.Popen')
    def test_malicious_domain_is_rejected_without_invoking_subprocess(self, mock_views_popen, mock_other_views_popen):
        malicious_domain = 'example.com;id'
        for view, mock_popen in ((cmd_lab3, mock_other_views_popen), (cmd_lab, mock_views_popen)):
            request = self.factory.post('/cmd', {'domain': malicious_domain, 'os': 'linux'})
            request.user = self.user

            response = view(request)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Something went wrong', response.content.decode())
            mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_vector_and_shell_false(self, mock_views_popen, mock_other_views_popen):
        mock_other_views_process = mock_other_views_popen.return_value
        mock_other_views_process.communicate.return_value = (b'lookup ok', b'')
        mock_views_process = mock_views_popen.return_value
        mock_views_process.communicate.return_value = (b'lookup ok', b'')

        for view, mock_popen in ((cmd_lab3, mock_other_views_popen), (cmd_lab, mock_views_popen)):
            request = self.factory.post('/cmd', {'domain': 'example.com', 'os': 'linux'})
            request.user = self.user

            response = view(request)

            self.assertEqual(response.status_code, 200)
            self.assertIn('lookup ok', response.content.decode())
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            self.assertEqual(args[0], ['dig', 'example.com'])
            self.assertFalse(kwargs['shell'])
