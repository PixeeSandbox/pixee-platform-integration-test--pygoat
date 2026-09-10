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
            domain=request.POST.get('domain')
            if not domain:
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            domain=domain.replace("https://www.",'').strip()
            if len(domain) > 253:
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            hostname_pattern = r"(?:localhost|(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63})"
            ipv4_pattern = r"(?:\d{1,3}\.){3}\d{1,3}"
            if not (
                re.fullmatch(hostname_pattern, domain)
                or (re.fullmatch(ipv4_pattern, domain) and all(0 <= int(part) <= 255 for part in domain.split('.')))
            ):
                output = "Invalid domain"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            os=request.POST.get('os')
            print(os)
            if(os=='win'):
                command_gEzs32aJ=["nslookup", domain]
            else:
                command_gEzs32aJ = ["dig", domain]
            try:
                process = subprocess.run(
                    command_gEzs32aJ,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True)
                data = process.stdout
                stderr = process.stderr
                if process.returncode != 0:
                    output = "Something went wrong"
                else:
                    output = data + stderr
                print(data + stderr)
            except (subprocess.SubprocessError, OSError):
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            print(output)
            return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
    else:
        return redirect('login')
