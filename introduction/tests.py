from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3ValidationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.username = 'cmdlabuser'
        self.password = 'StrongPass123!'
        User.objects.create_user(username=self.username, password=self.password)
        self.assertTrue(self.client.login(username=self.username, password=self.password))

    def test_rejects_malicious_domain_input(self):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;whoami',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'whoami')
