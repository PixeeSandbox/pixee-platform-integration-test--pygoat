from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='test-password',
        )

    def test_cmd_lab3_rejects_shell_metacharacters_in_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; whoami', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        self.assertNotIn('example.com; whoami', response.content.decode())
