from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest
from django.test import RequestFactory, TestCase

import introduction.views as views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd-user',
            password='password123',
        )

    def test_cmd_lab_valid_domain_uses_safe_popen_invocation(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen, patch(
            'introduction.views.render', return_value=HttpResponse('ok')
        ) as mock_render:
            mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        mock_render.assert_called_once()

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = views.cmd_lab(request)

        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
