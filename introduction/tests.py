from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_passes_domain_as_literal_argument(self, mock_popen, mock_render):
        domain = 'example.com; rm -rf /'
        process = Mock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process
        mock_render.return_value = Mock(name='response')

        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', domain])
        self.assertNotIn('shell', kwargs)
        mock_render.assert_called_once()
        self.assertEqual(response, mock_render.return_value)
