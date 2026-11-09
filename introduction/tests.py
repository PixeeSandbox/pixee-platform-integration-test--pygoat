from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            email='cmdlabuser@example.com',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Invalid domain', content)
        self.assertNotIn('uid=', content)
        self.assertNotIn('gid=', content)
