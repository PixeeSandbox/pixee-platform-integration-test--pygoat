from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_uses_argument_list_for_domain(self):
        user = get_user_model().objects.create_user(
            username='cmduser',
            password='strong-password-123'
        )
        self.client.force_login(user)

        malicious_domain = 'example.com; rm -rf /'

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'stdout', b'stderr')

            response = self.client.post('/cmd_lab', {
                'domain': malicious_domain,
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', malicious_domain],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertTrue(process.communicate.called)
