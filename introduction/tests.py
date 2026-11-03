from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab3_uses_list_popen_for_safe_domain(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        process = patch('introduction.other_views.subprocess.Popen')
        render_patch = patch('introduction.other_views.render', return_value=HttpResponse('rendered'))
        with process as popen_mock, render_patch as render_mock:
            popen_instance = popen_mock.return_value
            popen_instance.communicate.return_value = (b'lookup output', b'')

            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        self.assertEqual(popen_mock.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(popen_mock.call_args.kwargs.get('shell', False))
        render_mock.assert_called_once()

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        process = patch('introduction.other_views.subprocess.Popen')
        render_patch = patch('introduction.other_views.render', return_value=HttpResponse('rendered'))
        with process as popen_mock, render_patch as render_mock:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]['output'], 'Something went wrong')
