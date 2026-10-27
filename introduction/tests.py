from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd_user',
            password='testpass123',
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')
        mock_render.return_value = 'rendered-response'

        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response, 'rendered-response')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertEqual(mock_popen.call_args.kwargs['stdout'], views.subprocess.PIPE)
        self.assertEqual(mock_popen.call_args.kwargs['stderr'], views.subprocess.PIPE)
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2]['output'], 'lookup ok')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen, mock_render):
        mock_render.return_value = 'rendered-response'

        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com; id', 'os': 'linux'},
        )
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response, 'rendered-response')
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Invalid domain')
