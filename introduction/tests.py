from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertEqual(mock_popen.call_args.kwargs['shell'], False)
        self.assertIsInstance(mock_popen.call_args.args[0], list)
        mock_render.assert_called_once()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_invalid_input_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')

        for domain, os_value in [('example.com; id', 'linux'), ('example.com', 'mac')]:
            with self.subTest(domain=domain, os_value=os_value):
                request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_value})
                request.user = self.user

                response = cmd_lab3(request)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b'Something went wrong')
                mock_popen.assert_not_called()
                mock_render.assert_called_with(
                    request,
                    'Lab/CMD/cmd_lab.html',
                    {'output': 'Something went wrong'}
                )
                mock_popen.reset_mock()
                mock_render.reset_mock()
