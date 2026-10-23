from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest import mock

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')

    @mock.patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_domain_uses_argument_list_without_shell(self, mock_popen):
        process = mock.Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=mock.ANY,
            stderr=mock.ANY,
        )
        self.assertContains(response, 'lookup ok')

    @mock.patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')
