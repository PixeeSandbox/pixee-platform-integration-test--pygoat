from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123',
        )
        self.url = reverse('Command Injection Lab 3')

    def test_rejects_malicious_domain_without_calling_subprocess(self):
        self.client.force_login(self.user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post(
                self.url,
                {'domain': 'example.com;id', 'os': 'linux'},
            )

        self.assertContains(response, 'Invalid input')
        popen.assert_not_called()

    def test_accepts_valid_domain_and_uses_argument_list(self):
        self.client.force_login(self.user)
        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen:
            response = self.client.post(
                self.url,
                {'domain': 'example.com', 'os': 'linux'},
            )

        self.assertContains(response, 'example output')
        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
