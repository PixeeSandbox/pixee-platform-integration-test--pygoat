from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import ANY, Mock, patch

from introduction.views import cmd_lab


class CmdLabViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username='tester', password='password123')
        cls.factory = RequestFactory()

    def test_valid_domain_uses_argument_list_and_shell_disabled(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b'stdout', b'stderr')

        with patch('introduction.views.subprocess.Popen', return_value=process) as popen_mock:
            with patch('introduction.views.render', return_value=HttpResponse('rendered')) as render_mock:
                response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]['output'], 'stdoutstderr')

    def test_invalid_domain_is_rejected_before_subprocess_execution(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as popen_mock:
            with patch('introduction.views.render', return_value=HttpResponse('rendered')) as render_mock:
                response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_not_called()
        render_mock.assert_called_once()
        self.assertEqual(render_mock.call_args.args[2]['output'], 'Invalid domain')
