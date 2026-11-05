from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_injection_payload(self):
        malicious_domain = 'example.com;echo injected&&whoami'
        response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'linux'})
        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', content)
        self.assertNotIn(malicious_domain, content)
        self.assertNotIn('injected', content)
        self.assertNotIn('whoami', content)
