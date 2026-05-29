import hashlib
import ipaddress
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


def _is_valid_domain(raw_domain):
    if raw_domain is None:
        return None
    if raw_domain != raw_domain.strip():
        return None
    if not raw_domain:
        return None
    if any(ch.isspace() for ch in raw_domain):
        return None
    if '://' in raw_domain or '/' in raw_domain or '\\' in raw_domain or '?' in raw_domain or '#' in raw_domain or '@' in raw_domain:
        return None
    try:
        return str(ipaddress.ip_address(raw_domain))
    except ValueError:
        pass
    domain = raw_domain.rstrip('.')
    if not domain or len(domain) > 253:
        return None
    labels = domain.split('.')
    hostname_pattern = r'(?!-)[A-Za-z0-9-]{1,63}(?<!-)'
    if len(labels) == 1:
        return domain if re.fullmatch(hostname_pattern, domain) else None
    if all(re.fullmatch(hostname_pattern, label) for label in labels):
        return domain
    return None




@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            domain=request.POST.get('domain','')
            target_os=request.POST.get('os')
            logging.debug("cmd_lab3 os=%s", target_os)
            domain = _is_valid_domain(domain)
            if not domain:
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            if(target_os=='win'):
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
