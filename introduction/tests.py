from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.render')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_render, mock_popen):
        request = self.factory.post('/cmd-lab/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'}
        )
        self.assertEqual(response, mock_render.return_value)

    @patch('introduction.views.subprocess.Popen')
    @patch('introduction.views.render')
    def test_cmd_lab_passes_hostname_as_argument_without_shell(self, mock_render, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'dns output', b'')
        request = self.factory.post('/cmd-lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = type('User', (), {'is_authenticated': True})()

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request, 'Lab/CMD/cmd_lab.html', {'output': 'dns output'}
        )
        self.assertEqual(response, mock_render.return_value)
