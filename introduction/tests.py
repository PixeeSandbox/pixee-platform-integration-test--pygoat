from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            email='tester@example.com',
            password='testpass123',
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        self.assertIn(b'example output', response.content)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)
