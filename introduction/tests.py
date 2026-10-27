from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from . import other_views


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdtestuser',
            password='StrongPass123!'
        )

    def test_cmd_lab3_rejects_malicious_domain_before_execution(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; cat /etc/passwd',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as popen_mock:
            response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'nslookup')
        self.assertNotContains(response, 'dig')
        popen_mock.assert_not_called()
