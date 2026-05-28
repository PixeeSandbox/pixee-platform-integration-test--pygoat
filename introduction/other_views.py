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
#*****************************************Login and Registration****************************************************#

@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            domain=request.POST.get('domain')
            if not domain:
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            domain = domain.strip()
            domain = re.sub(r'^(?:https?://)?(?:www\.)?', '', domain, flags=re.IGNORECASE)
            if any(ch.isspace() for ch in domain):
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            domain = domain.split('/', 1)[0].split('?', 1)[0].split('#', 1)[0].strip()
            if domain.startswith('[') and domain.endswith(']'):
                domain = domain[1:-1]
            if not domain:
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            target_os=request.POST.get('os')
            print(target_os)
            valid_domain = False
            try:
                ipaddress.ip_address(domain)
                valid_domain = True
            except ValueError:
                if re.fullmatch(r"(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*\.?", domain):
                    valid_domain = True
            if not valid_domain:
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            command = ["nslookup", domain] if target_os=='win' else ["dig", domain]
            try:
                process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                data = process.stdout.decode('utf-8')
                stderr = process.stderr.decode('utf-8')
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
