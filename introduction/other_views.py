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


def _normalize_domain(domain):
    if not domain:
        return ""
    domain = domain.strip()
    domain = re.sub(r'^(?:https?://)?(?:www\.)?', '', domain, flags=re.IGNORECASE)
    domain = domain.split('/', 1)[0]
    domain = domain.split('?', 1)[0]
    domain = domain.split('#', 1)[0]
    return domain.rstrip('.')


def _is_valid_domain(domain):
    if not domain or len(domain) > 253:
        return False
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        pass

    labels = domain.split('.')
    if any(not label or len(label) > 63 for label in labels):
        return False

    label_pattern = r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?'
    return all(re.fullmatch(label_pattern, label) for label in labels)


@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            try:
                domain = _normalize_domain(request.POST.get('domain', ''))
                client_os = request.POST.get('os')
                print(client_os)
                if not _is_valid_domain(domain):
                    raise ValueError("Invalid domain")
                if client_os == 'win':
                    command = ["nslookup", domain]
                elif client_os == 'linux':
                    command = ["dig", domain]
                else:
                    raise ValueError("Invalid os")
                process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                stdout = process.stdout.decode('utf-8')
                stderr = process.stderr.decode('utf-8')
                # res = json.loads(data)
                # print("Stdout\n" + data)
                output = stdout + stderr
                print(stdout + stderr)
            except:
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            print(output)
            return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
    else:
        return redirect('login')
