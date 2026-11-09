from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CommandInjectionTests(TestCase):
    def test_cmd_lab3_rejects_invalid_domain(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='testpass123')
        client = Client()
        client.force_login(user)

        response = client.post('/cmd_lab3', {
            'domain': 'example.com; cat /etc/passwd',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'example.com; cat /etc/passwd')
