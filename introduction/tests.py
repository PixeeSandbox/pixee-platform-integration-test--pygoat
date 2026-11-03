from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction import other_views
from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    def test_cmd_lab3_uses_argv_and_disables_shell_for_untrusted_domain(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={
                'domain': 'example.com; whoami',
                'os': 'linux',
            },
        )
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen, \
                patch('introduction.other_views.render', return_value=HttpResponse('ok')):
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; whoami'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
