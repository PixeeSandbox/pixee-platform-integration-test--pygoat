from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='StrongPass123!')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})

        self.assertContains(response, 'Invalid domain')
        mocked_popen.assert_not_called()
