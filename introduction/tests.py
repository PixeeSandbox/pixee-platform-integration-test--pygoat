from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='password123')

    def _post_cmd_lab(self, domain):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': 'win'})
        request.user = self.user
        return cmd_lab(request)

    def test_cmd_lab_rejects_leading_hyphen_domain(self):
        response = self._post_cmd_lab('-foo.com')
        self.assertEqual(response.status_code, 400)

    def test_cmd_lab_rejects_empty_label_domain(self):
        response = self._post_cmd_lab('example..com')
        self.assertEqual(response.status_code, 400)

    def test_cmd_lab_rejects_trailing_dot_domain(self):
        response = self._post_cmd_lab('example.com.')
        self.assertEqual(response.status_code, 400)
