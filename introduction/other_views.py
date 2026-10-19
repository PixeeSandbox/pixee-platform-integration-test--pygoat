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


def _is_valid_lookup_target(domain):
    domain = domain.strip().rstrip('.')
    if not domain or len(domain) > 253:
        return False
    ipv4_pattern = r"(?:\d{1,3}\.){3}\d{1,3}"
    if re.fullmatch(ipv4_pattern, domain):
        return all(0 <= int(part) <= 255 for part in domain.split('.'))
    labels = domain.split('.')
    if any(not label or len(label) > 63 for label in labels):
        return False
    return all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label) for label in labels)


@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            domain=request.POST.get('domain', '')
            domain=domain.replace("https://www.", '').strip()
            os=request.POST.get('os')
            print(os)
            if not _is_valid_lookup_target(domain):
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            if(os=='win'):
                command_69mrcfVM=["nslookup", domain]
            else:
                command_69mrcfVM = ["dig", domain]
            try:
                process = subprocess.run(
                    command_69mrcfVM,
                    capture_output=True,
                    text=True,
                    shell=False)
                output = process.stdout + process.stderr
                print(output)
            except:
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            print(output)
            return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
    else:
        return redirect('login')
