from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('ok')
        mock_run.return_value.stdout = 'answer'
        mock_run.return_value.stderr = 'warning'
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True, check=False)
        self.assertEqual(mock_render.call_args[0][2]['output'], 'answerwarning')
        self.assertEqual(response.status_code, 200)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_hostname_without_subprocess(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Something went wrong')
        self.assertEqual(response.status_code, 200)
