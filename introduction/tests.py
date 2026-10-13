from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd_lab3_user',
            password='password123',
        )

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com;whoami', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
