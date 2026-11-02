from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab3_valid_hostname_uses_argument_list(self):
        request = self.factory.post('/cmd_lab', {'domain': ' https://www.example.com ', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render'
        ) as mock_render:
            process = MagicMock()
            process.communicate.return_value = (b'lookup output', b'')
            mock_popen.return_value = process
            mock_render.return_value = HttpResponse('ok')

            response = other_views.cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)

    def test_cmd_lab3_rejects_injection_payload_before_subprocess(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; cat /etc/passwd', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render'
        ) as mock_render:
            mock_render.return_value = HttpResponse('invalid')

            response = other_views.cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertIn('Invalid domain', mock_render.call_args[0][2]['output'])
        self.assertEqual(response.status_code, 200)
