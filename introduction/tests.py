from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
        )

    def test_cmd_lab3_rejects_shell_metacharacters_in_domain(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')

    def test_cmd_lab3_rejects_invalid_os_selector(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'mac'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
