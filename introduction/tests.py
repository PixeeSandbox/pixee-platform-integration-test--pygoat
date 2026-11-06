from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmdlabuser', password='StrongPass123!')
        self.assertTrue(self.client.login(username='cmdlabuser', password='StrongPass123!'))

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch('introduction.other_views.subprocess.Popen') as mocked_popen:
            response = self.client.post(reverse('Command Injection Lab 3'), {
                'domain': 'example.com;id',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mocked_popen.assert_not_called()
