from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_cmd_lab3_rejects_malicious_domain_before_popen(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com;rm -rf /', 'os': 'win'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            with patch('introduction.other_views.render', return_value=HttpResponse('Something went wrong')):
                response = cmd_lab3(request)

        self.assertEqual(response.content, b'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argv_list_without_shell(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com', 'os': 'win'}
        )
        request.user = self.user

        process = patch('introduction.other_views.subprocess.Popen')
        with process as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'lookup output', b'')
            with patch('introduction.other_views.render', return_value=HttpResponse('ok')):
                response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', called_kwargs)
