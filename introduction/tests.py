from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = type('User', (), {'is_authenticated': True})()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list(self, mock_run, mock_render):
        mock_run.return_value.stdout = 'resolved\n'
        mock_run.return_value.stderr = ''
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, check=False)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'resolved\n'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'Something went wrong')
        mock_run.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
