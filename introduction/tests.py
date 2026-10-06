from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_domain_uses_argv_list(self, mock_popen, mock_render):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')
        mock_render.return_value = HttpResponse('rendered')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'example output'})

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rendered')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_count, 0)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
