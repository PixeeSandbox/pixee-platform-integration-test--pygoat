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
#*****************************************Login and Registration****************************************************#

@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            domain=(request.POST.get('domain') or '')
            domain=domain.replace("https://www.",'')
            os=request.POST.get('os')
            print(os)
            if not domain or len(domain) > 253:
                return render(request,'Lab/CMD/cmd_lab.html',{"output":"Invalid domain supplied"})
            if domain != 'localhost':
                ipv4_parts = domain.split('.')
                if len(ipv4_parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ipv4_parts):
                    pass
                else:
                    labels = domain.split('.')
                    if len(labels) < 2 or any(not re.fullmatch(r'[A-Za-z0-9-]{1,63}', label) or label.startswith('-') or label.endswith('-') for label in labels):
                        return render(request,'Lab/CMD/cmd_lab.html',{"output":"Invalid domain supplied"})
            if(os=='win'):
                command_HZXZQIUI=['nslookup', domain]
            else:
                command_HZXZQIUI = ['dig', domain]
            try:
                # output=subprocess.check_output(command_HZXZQIUI,shell=True,encoding="UTF-8")
                process = subprocess.Popen(
                    command_HZXZQIUI,
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
