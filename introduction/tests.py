from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmd-lab-test', password='test-password')
        self.client.force_login(self.user)

    def test_rejects_invalid_domain_without_launching_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; whoami',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        popen.assert_not_called()
