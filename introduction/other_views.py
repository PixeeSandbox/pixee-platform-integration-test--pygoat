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
import ipaddress
from urllib.parse import urlsplit
#*****************************************Login and Registration****************************************************#

@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            domain = (request.POST.get('domain') or '').strip()
            os=request.POST.get('os')
            print(os)

            try:
                raw_domain = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', domain, count=1)
                raw_domain = raw_domain.split('/', 1)[0].split('?', 1)[0].split('#', 1)[0].strip()
                if raw_domain.startswith('[') and ']' in raw_domain:
                    raw_domain = raw_domain[1:raw_domain.index(']')]
                else:
                    raw_domain = raw_domain.rstrip('.')
                if not raw_domain:
                    raise ValueError()
                try:
                    ipaddress.ip_address(raw_domain)
                    domain = raw_domain
                except ValueError:
                    parsed_domain = urlsplit(f'//{raw_domain}')
                    if parsed_domain.username or parsed_domain.password:
                        raise ValueError()
                    parsed_domain.port
                    domain = parsed_domain.hostname or ''
                    if not domain:
                        raise ValueError()
                    domain = domain.encode('idna').decode('ascii')
                    hostname_regex = r'(?:[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?)(?:\.(?:[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?))*\.?'
                    if domain.startswith('-') or not re.fullmatch(hostname_regex, domain):
                        raise ValueError()
            except (ValueError, UnicodeError):
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})

            try:
                if(os=='win'):
                    process = subprocess.run([
                        "nslookup",
                        domain],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                else:
                    process = subprocess.run([
                        "dig",
                        domain],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                stdout, stderr = process.stdout, process.stderr
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
