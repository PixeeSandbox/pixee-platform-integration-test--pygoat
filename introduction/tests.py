from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='secure-password123')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_command_injection_domain(self):
        response = self.client.post('/cmd_lab', {'domain': 'google.com && dir', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
