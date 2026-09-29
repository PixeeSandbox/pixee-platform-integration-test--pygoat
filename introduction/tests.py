from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123'
        )

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain_without_running_subprocess(self, mock_run):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout=b'Lookup complete\n', stderr=b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Lookup complete', response.content.decode('utf-8'))
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell'))
