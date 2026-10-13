from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')

    def test_cmd_lab_rejects_malicious_domain_without_running_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; id',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mocked_popen.assert_not_called()
