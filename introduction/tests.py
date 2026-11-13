from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmdtest', password='test-password')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab 3')

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_hostname_with_shell_metacharacters(self, popen):
        response = self.client.post(self.url, {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_runs_lookup_with_hostname_as_separate_argument(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)
        self.assertIn('lookup output', response.content.decode('utf-8'))
