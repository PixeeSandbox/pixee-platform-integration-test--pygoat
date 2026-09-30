from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertContains(response, 'Invalid domain')
