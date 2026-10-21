from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain(self):
        user = User.objects.create_user(username='cmdlab3user', password='StrongPass123!')
        self.client.force_login(user)

        response = self.client.post(
            reverse('cmd_lab3'),
            {'domain': 'example.com;whoami', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertContains(response, 'Invalid domain')
