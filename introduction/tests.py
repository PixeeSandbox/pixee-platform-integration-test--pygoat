from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters_in_domain(self):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; whoami',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'whoami')
