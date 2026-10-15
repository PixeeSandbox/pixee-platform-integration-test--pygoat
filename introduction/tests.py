from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    def test_cmd_lab3_accepts_normal_hostname(self):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Invalid domain')

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'whoami')
