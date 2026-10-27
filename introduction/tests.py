from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab-user',
            password='password123'
        )

    @patch('introduction.views.render', return_value=HttpResponse('ok'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'example output', b'')
        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.render', return_value=HttpResponse('ok'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
