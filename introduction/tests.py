from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123'
        )

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen, patch(
            'introduction.views.render', return_value=HttpResponse('ok')
        ):
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_hostname(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen, patch(
            'introduction.views.render', return_value=HttpResponse('ok')
        ):
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'example output', b'')
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen_args, popen_kwargs = mock_popen.call_args
        self.assertEqual(popen_args[0], ['dig', 'example.com'])
        self.assertFalse(popen_kwargs.get('shell', True))
