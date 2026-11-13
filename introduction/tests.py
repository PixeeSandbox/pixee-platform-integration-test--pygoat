from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3CommandInjectionTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_invalid_domains_without_starting_process(self, popen):
        for domain in ('example.com; id', '-example.com'):
            with self.subTest(domain=domain):
                response = self.client.post('/cmd_lab3', {'domain': domain, 'os': 'win'})
                self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
