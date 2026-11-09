from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_rejects_malicious_domain_input(self):
        User = get_user_model()
        user = User.objects.create_user(username='cmdlab3_user', password='Password123!')
        self.client.force_login(user)

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com; cat /etc/passwd',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<pre>Invalid domain</pre>', html=False)
