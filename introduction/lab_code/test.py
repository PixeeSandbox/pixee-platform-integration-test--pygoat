'''
import subprocess, json


cmd_args = ["pwd"]
process = subprocess.run(
    cmd_args,
    capture_output=True,
    text=True)
stdout = process.stdout
stderr = process.stderr
# res = json.loads(data)
# print("Stdout\n" + data)
print((stdout or "") + (stderr or ""))
'''
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
