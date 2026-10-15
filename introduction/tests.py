from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from introduction import other_views


class CmdLab3SecurityTests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = User.objects.create_user(username='testuser', password='password')
        request = RequestFactory().post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})
        request.user = user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
