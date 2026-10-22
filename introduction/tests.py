from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain_input(self):
        User = get_user_model()
        User.objects.create_user(username="cmdtester", password="secure-password")
        client = Client()
        self.assertTrue(client.login(username="cmdtester", password="secure-password"))

        response = client.post(
            reverse('Command Injection Lab'),
            {
                'domain': 'example.com; cat /etc/passwd',
                'os': 'linux',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
