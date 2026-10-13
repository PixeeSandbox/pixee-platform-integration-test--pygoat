from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

import introduction.other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;whoami', 'os': 'win'})
        request.user = self.user
        response = Mock()
        mock_render.return_value = response

        result = introduction.other_views.cmd_lab3(request)

        self.assertIs(result, response)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_hostname(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process
        response = Mock()
        mock_render.return_value = response

        result = introduction.other_views.cmd_lab3(request)

        self.assertIs(result, response)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'example output'})
