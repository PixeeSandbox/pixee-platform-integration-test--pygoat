'''
import subprocess, json


cmd_str = "pwd; ls"
process = subprocess.Popen(
    cmd_str,
    shell=True,
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
data = stdout.decode('utf-8')
stderr = stderr.decode('utf-8')
# res = json.loads(data)
# print("Stdout\n" + data)
print(data + stderr)
'''
if __name__ == "__main__":
    import yaml, subprocess
    stream = open('/home/fox/test.yaml', 'r')
    data = yaml.load(stream)

    '''
    stdout, stderr = data.communicate()
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    '''
    print(data + "\n")
    # print(stdout + "\n")
    # print(stderr + "\n")

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("introduction.other_views.subprocess.Popen")
    @patch("introduction.other_views.render")
    def test_cmd_lab3_uses_argv_and_disables_shell(self, mock_render, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b"ok", b"")
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse("ok")

        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "https://www.example.com", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(response.content, b"ok")

    @patch("introduction.other_views.subprocess.Popen")
    @patch("introduction.other_views.render")
    def test_cmd_lab3_rejects_shell_metacharacters_before_execution(self, mock_render, mock_popen):
        mock_render.return_value = HttpResponse("Something went wrong")

        request = self.factory.post(
            "/cmd_lab3",
            {"domain": "example.com&&id", "os": "win"},
        )
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.content, b"Something went wrong")
