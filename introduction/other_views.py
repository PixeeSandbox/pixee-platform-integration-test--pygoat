import hashlib
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import  FAANG, AF_session_id,info,login,comments,authLogin, tickits, sql_lab_table,Blogs,CF_user,AF_admin
from django.core import serializers
from requests.structures import CaseInsensitiveDict
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import UserCreationForm
import random
import string
import os
from hashlib import md5
import datetime
from .forms import NewUserForm
from django.contrib import messages
#*****************************************Lab Requirements****************************************************#

from .models import  FAANG,info,login,comments,otp
from random import randint
from xml.dom.pulldom import parseString, START_ELEMENT
from xml.sax.handler import feature_external_ges
from xml.sax import make_parser
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.template.loader import render_to_string
import subprocess
import pickle
import base64
import yaml
import json
from dataclasses import dataclass
import uuid
from .utility import filter_blog, customHash
import jwt
from PIL import Image,ImageMath
import base64
from io import BytesIO
from argon2 import PasswordHasher
import logging
import requests
import re


def _is_safe_lookup_target(value):
    if not value:
        return False
    if re.search(r"\s", value):
        return False
    if value == "localhost":
        return True
    if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", value):
        return all(0 <= int(part) <= 255 for part in value.split("."))
    if len(value) > 253:
        return False
    labels = value.split(".")
    if any(not label or len(label) > 63 for label in labels):
        return False
    if not all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label) for label in labels):
        return False
    return True
#*****************************************Login and Registration****************************************************#

@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            domain=request.POST.get('domain')
            domain=domain.replace("https://www.",'')
            if not _is_safe_lookup_target(domain):
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            os=request.POST.get('os')
            print(os)
            if(os=='win'):
                command=["nslookup", domain]
            else:
                command = ["dig", domain]
            try:
                # output=subprocess.check_output(command,shell=True,encoding="UTF-8")
                process = subprocess.Popen(
                    command,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                data = stdout.decode('utf-8')
                stderr = stderr.decode('utf-8')
                # res = json.loads(data)
                # print("Stdout\n" + data)
                output = data + stderr
                print(data + stderr)
            except:
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            print(output)
            return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
    else:
        return redirect('login')
