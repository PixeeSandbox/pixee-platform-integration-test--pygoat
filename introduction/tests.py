from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'example.com; id', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain input')
