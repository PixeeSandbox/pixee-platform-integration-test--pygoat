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


def _is_valid_cmd_lab3_target(value):
    if not value:
        return False

    value = value.strip()
    if not value or any(ch.isspace() for ch in value):
        return False
    if any(ch in value for ch in [';', '&', '|', '$', '`', '\\', '<', '>', '(', ')', '{', '}', '[', ']', '\"', "'", '*', '?', '~', '!']):
        return False

    def _is_valid_ipv4(candidate):
        parts = candidate.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit() or (part.startswith('0') and len(part) > 1):
                return False
            if not 0 <= int(part) <= 255:
                return False
        return True

    def _is_valid_hostname(candidate):
        if len(candidate) > 253 or candidate.startswith('.') or candidate.endswith('.'):
            return False
        labels = candidate.split('.')
        if not labels:
            return False
        for label in labels:
            if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label):
                return False
        return True

    def _is_valid_ipv6(candidate):
        if candidate.count('::') > 1:
            return False
        if candidate == '::':
            return True

        head, sep, tail = candidate.partition('::')
        if sep:
            head_parts = head.split(':') if head else []
            tail_parts = tail.split(':') if tail else []
            if '' in head_parts or '' in tail_parts:
                return False
            parts = head_parts + tail_parts
            ipv4_tail = False
            if parts and '.' in parts[-1]:
                if not _is_valid_ipv4(parts[-1]):
                    return False
                ipv4_tail = True
                parts = parts[:-1]
            if any('.' in part for part in parts):
                return False
            if not all(re.fullmatch(r'[A-Fa-f0-9]{1,4}', part) for part in parts):
                return False
            hextet_count = len(parts) + (2 if ipv4_tail else 0)
            return hextet_count < 8

        parts = candidate.split(':')
        if '' in parts:
            return False
        ipv4_tail = False
        if parts and '.' in parts[-1]:
            if not _is_valid_ipv4(parts[-1]):
                return False
            ipv4_tail = True
            parts = parts[:-1]
        if any('.' in part for part in parts):
            return False
        if not all(re.fullmatch(r'[A-Fa-f0-9]{1,4}', part) for part in parts):
            return False
        return len(parts) + (2 if ipv4_tail else 0) == 8

    if ':' in value:
        return _is_valid_ipv6(value)

    if _is_valid_ipv4(value):
        return True

    return _is_valid_hostname(value)


@csrf_exempt
def cmd_lab3(request):
    if request.user.is_authenticated:
        if (request.method=="POST"):
            domain=request.POST.get('domain')
            if domain is None:
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            domain=domain.replace("https://www.",'').strip()
            if not _is_valid_cmd_lab3_target(domain):
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            os=request.POST.get('os')
            print(os)
            if(os=='win'):
                command=["nslookup", domain]
            else:
                command = ["dig", domain]
            try:
                process = subprocess.run(command, capture_output=True, text=True)
                data = process.stdout
                stderr = process.stderr
                output = data + stderr
                print(data + stderr)
            except:
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            print(output)
            return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
    else:
        return redirect('login')
